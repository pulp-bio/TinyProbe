from pathlib import Path
import time
import functools

import numpy as np

from src.config.models import TPConfig, TPVisualizationConfig


rx_mappings = {
    "vermon_ndt": np.array(
        [
            29,
            9,
            27,
            7,
            25,
            4,
            23,
            11,
            21,
            5,
            26,
            3,
            30,
            1,
            28,
            0,
            31,
            2,
            17,
            15,
            16,
            14,
            19,
            13,
            18,
            12,
            20,
            10,
            22,
            8,
            24,
            6,
        ]
    )
}


def print_execution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        print(f"  Done in {t1 - t0:.3f} seconds.")
        return result

    return wrapper


@print_execution_time
def import_packages():
    global Fraction
    from fractions import Fraction

    global ss, trange
    import scipy.signal as ss
    from tqdm import trange

    global Transducer, parse_bitstream_jax, BFCartesianRealTime, ImageSettings
    from src.pybf.pybf.transducer import Transducer
    from src.bitstream_parser import parse_bitstream_jax
    from src.pybf.scripts.beamformer_cartesian_realtime import BFCartesianRealTime
    from src.pybf.pybf.image_settings import ImageSettings


@print_execution_time
def load_configs(vis_config_path: str) -> tuple[TPConfig, TPVisualizationConfig]:
    with open(vis_config_path, "r") as f:
        vis_config = TPVisualizationConfig.model_validate_json(f.read())

    config_path = Path(vis_config_path).parent / vis_config.config

    with open(config_path, "r") as f:
        config = TPConfig.model_validate_json(f.read())

    return config, vis_config


@print_execution_time
def load_data(
    config: TPConfig, vis_config: TPVisualizationConfig, file_path: str
) -> np.ndarray:
    if vis_config.rx_mapping not in rx_mappings:
        raise ValueError(f"Unknown RX mapping: {vis_config.rx_mapping!r}")

    if file_path.endswith(".npy"):
        data = np.load(file_path)
        data = data.tobytes()
    else:
        with open(file_path, "rb") as f:
            data = f.read()

    n_shots_rx = config.fpga.num_shots * config.tx.strategy.num_planewaves

    if len(data) % n_shots_rx != 0:
        raise ValueError(
            f"Data length {len(data)} is not a multiple of number of shots {n_shots_rx}."
        )

    bytes_per_shot = int(len(data) / n_shots_rx)

    def parse_shot(data_shot):
        return parse_bitstream_jax(
            data_shot,
            num_shots=n_shots_rx,
            read_size_samples=config.fpga.fifo_depth,
            bits_per_sample=10,
            n_activ_ch=len(config.fpga.lvds_lanes) * 2,
            bits_per_sample_out=16,
            bit_slip_arr=[-2] * 16,
            dbg_msgs=False,
        )

    data = np.frombuffer(data, dtype=np.uint8).reshape((n_shots_rx, bytes_per_shot))
    data = np.apply_along_axis(parse_shot, 1, data)
    data = data[:, :, rx_mappings[vis_config.rx_mapping], :][0]

    return data


@print_execution_time
def preprocess_data(
    config: TPConfig, vis_config: TPVisualizationConfig, data: np.ndarray
) -> np.ndarray:
    if vis_config.preprocess.flatten_samples:
        data[:, :, : vis_config.preprocess.flatten_samples] = np.mean(
            data[:, :, vis_config.preprocess.flatten_samples :], axis=2, keepdims=True
        )

    if vis_config.preprocess.median_filter_samples:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                data[i, j, :] = ss.medfilt(
                    data[i, j, :],
                    kernel_size=vis_config.preprocess.median_filter_samples,
                )

    f_sampling = 30e6 if config.fpga.afe_clk_hispeed else 10e6
    f_pass = [
        vis_config.preprocess.f_pass_frac[0] * config.tx.pulse_freq_hz,
        vis_config.preprocess.f_pass_frac[1] * config.tx.pulse_freq_hz,
    ]

    # Normalize frequencies to the Nyquist frequency
    nyq = f_sampling / 2
    wp = np.array(f_pass) / nyq

    # Design the Chebyshev type II filter
    # filter_result = ss.iirfilter(
    #     N=5,
    #     Wn=wp,
    #     rs=vis_config.preprocess.gain_stop_db,
    #     btype="band",
    #     analog=False,
    #     ftype="cheby2",
    #     output="ba",
    # )
    filter_result = ss.butter(
        N=5,
        Wn=wp,
        btype="bandpass",
        analog=False,
        output="ba",
    )
    if filter_result is None:
        raise ValueError("Filter design failed.")

    data = ss.filtfilt(filter_result[0], filter_result[1], data, axis=2)

    return data


@print_execution_time
def beamform_data(
    config: TPConfig, vis_config: TPVisualizationConfig, data: np.ndarray
) -> np.ndarray:
    f_sampling = 30e6 if config.fpga.afe_clk_hispeed else 10e6
    frac = Fraction(vis_config.beamform.scaling).limit_denominator(100)
    trans = Transducer(
        num_of_x_elements=config.tx.num_elems,
        x_pitch=config.tx.pitch_m,
        f_central_hz=config.tx.pulse_freq_hz,
        bandwidth_hz=config.tx.pulse_freq_hz,
    )
    trans.set_active_elements(list(range(len(config.fpga.lvds_lanes) * 2)))
    img_config = ImageSettings(
        vis_config.beamform.x_range_cm[0] / 100,
        vis_config.beamform.x_range_cm[1] / 100,
        vis_config.beamform.z_range_cm[0] / 100,
        vis_config.beamform.z_range_cm[1] / 100,
        5,
        trans,
    )
    bf = BFCartesianRealTime(
        f_sampling,
        config.tx.strategy.as_tuple(),
        trans,
        frac.denominator,
        frac.numerator,
        vis_config.beamform.resolution_px,
        img_config,
        db_range=vis_config.beamform.db_range,
        start_time=-6.1e-6,
        correction_time_shift=vis_config.beamform.correction_shift_us * 1e-6,
        alpha_fov_apod=vis_config.beamform.fov_deg,
    )

    img_data = data.reshape(
        (
            config.fpga.num_shots,
            config.tx.strategy.num_planewaves,
            data.shape[1],
            data.shape[2],
        )
    )

    start_idx = (
        vis_config.beamform.indexes[0]
        if vis_config.beamform.indexes[0] >= 0
        else len(img_data) + vis_config.beamform.indexes[0]
    )
    end_idx = (
        vis_config.beamform.indexes[1]
        if vis_config.beamform.indexes[1] >= 0
        else len(img_data) + vis_config.beamform.indexes[1]
    ) + 1

    if start_idx < 0 or start_idx > len(img_data):
        raise ValueError(f"Invalid start index: {vis_config.beamform.indexes[0]}")
    if end_idx < 0 or end_idx > len(img_data):
        raise ValueError(f"Invalid end index: {vis_config.beamform.indexes[1]}")

    def parse_image(image_data):
        return bf.beamform(image_data, core_type="numba")

    # Apply beamforming to each shot
    img_data = np.array(
        [
            parse_image(img_data[i])
            for i in trange(
                start_idx,
                end_idx,
                desc="Beamforming",
                unit="shots",
            )
        ]
    )

    return img_data
