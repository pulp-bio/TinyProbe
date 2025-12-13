import math
import logging

import numpy as np

from ..models import TPFPGAConfig, TPAFEConfig, TPTXConfig, TPConfig
from ...command.sequence import CommandSequence
from ...command.models import (
    SwitchSpiMux,
    ControlPower,
    WriteFPGAReg,
    TriggerShot,
    SleepMs,
)
from ...pybf.pybf.transducer import Transducer
from ...drivers.hal.fpga import TP_HAL_FPGA
from ...drivers.hal.afe5832lp import TP_HAL_AFE5832LP
from ...drivers.hal.tx7332 import TP_HAL_TX7332
from ...communication.communication import CommunicationInterface

log = logging.getLogger("tp").getChild("flows").getChild("configure")


fpga = TP_HAL_FPGA()
tx = TP_HAL_TX7332()
afe = TP_HAL_AFE5832LP()
num_packets = -1
tx_delays = np.zeros((0, 0))
tx_delays_cycles = np.zeros(0)


RX_MAPPING = np.array(
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
TX_MAPPING = np.array(
    [
        16,
        12,
        0,
        14,
        2,
        10,
        4,
        30,
        6,
        28,
        8,
        26,
        22,
        24,
        18,
        20,
        19,
        21,
        23,
        25,
        7,
        27,
        1,
        29,
        3,
        31,
        9,
        5,
        11,
        17,
        13,
        15,
    ]
)


def fpga_settings(config: TPFPGAConfig) -> CommandSequence:
    global num_packets

    num_packets = math.ceil(config.fifo_depth * 20 * len(config.lvds_lanes) / 8 / 1000)
    log.info(f"{num_packets = }")

    result = fpga.default_config(
        active_lvds_lanes=config.lvds_lanes,
        sensing_depth_samples=config.fifo_depth,
        meas_period_ms=config.shot_period_ms,
        n_acquisitions=config.num_shots,
        afe_clk_high_speed=config.afe_clk_hispeed,
        tx_bf_clk_high_speed=config.txbf_clk_hispeed,
        fpga_core_clk_high_speed=config.fpga_clk_hispeed,
        afe_start_capt_delay_us=config.afe_startcapt_delay_us,
    )
    fpga.set_mcu_interrupt_src(source=config.mcu_interrupt_src)
    result.add_command(fpga.get_cmd_sequence(from_history=True))

    log.info(f"Got FPGA command sequence with {len(result.commands)} commands")

    return result


def tx_settings(config: TPTXConfig) -> CommandSequence:
    global tx_delays, tx_delays_cycles

    trans = Transducer(
        num_of_x_elements=config.num_elems,
        x_pitch=config.pitch_m,
        f_central_hz=config.pulse_freq_hz,
        bandwidth_hz=config.pulse_freq_hz,
    )

    el_coords_x = trans.elements_coords[0, :] - trans.elements_coords[0, :].min()
    pw_angles_rad = np.radians(
        np.linspace(
            -config.strategy.max_angle,
            config.strategy.max_angle,
            config.strategy.num_planewaves,
        )
    ).reshape(-1, 1)
    tx_delays = (
        np.multiply(el_coords_x, np.sin(np.abs(pw_angles_rad)))
        / config.speed_of_sound_m_s
    )
    neg_ang_mask = np.sign(pw_angles_rad.flatten()) == -1
    tx_delays[neg_ang_mask, :] = tx_delays[neg_ang_mask, ::-1]

    # print(tx_delays, pw_angles_rad)

    tx_delays_cycles = tx_delays * fpga.tx_bf_clk
    if np.max(tx_delays_cycles) > 2**12:
        bf_clk_div = np.ceil(np.log2(np.max(tx_delays_cycles) / 2**12))
    else:
        bf_clk_div = 0
    if bf_clk_div > 5 or bf_clk_div < 0:
        raise ValueError(
            f"Calculated beamforming clock divider {bf_clk_div} is out of range [0, 5]."
        )

    tx.tx_bf_clk = fpga.tx_bf_clk
    tx.set_bf_clk_divider(factor=bf_clk_div)
    result = tx.default_config(
        n_pulses=config.num_pulses,
        pulse_freq_hz=int(config.pulse_freq_hz),
        tx_start_delay_us=5,
        tr_sw_delay_us=1.1,  # type: ignore
    )
    tx_delays_cycles = np.round(tx_delays_cycles)

    result.add_command([SwitchSpiMux(mux_code=3)])
    for id in range(tx_delays.shape[0]):
        tx.set_delays_s(tx_delays[id][TX_MAPPING], dp_id=id)
        # TODO: Check if we need to send 4 delay tables at a time
    tx.set_delay_prof_id(dp_id=int(tx_delays.shape[0] + 1) - 1)
    result.add_command(tx.get_cmd_sequence(from_history=True))
    tx.load_profile()
    result.add_command(tx.get_cmd_sequence())

    log.info(f"Got TX command sequence with {len(result.commands)} commands")
    return result


def afe_settings(
    config: TPAFEConfig, config_fpga: TPFPGAConfig
) -> tuple[CommandSequence, CommandSequence, CommandSequence, CommandSequence]:
    afe.set_fixed_gain(config.fixed_gain_atten)

    result_a = afe.get_cmd_sequence(from_history=True)

    afe.set_test_pattern(pattern=config.test_pattern)

    gain_step_period_us = afe.configure_tgc(
        start_db=config.tgc.start_db,
        stop_db=config.tgc.stop_db,
        slope_db_per_us=config.tgc.slope_db_per_us,
    )

    result_b = afe.get_cmd_sequence(from_history=True)

    result_c = fpga.set_tgc_settings(
        gain_step_period_us=gain_step_period_us,  # type: ignore
        start_delay_us=2,
        capture_time_us=200,
        finish_delay_us=10,
        match_with_wavegen=False,
    )

    if config.configure_lowpower:
        afe.set_low_power_mode()

    afe.set_lna_gain(config.lna_gain_db)
    afe.set_pga_gain(config.pga_gain_db)
    afe.set_lpf_freq(config.lpf_freq_mhz)
    afe.set_lna_hpf_freq(config.hpf_freq_khz)
    afe.enable_channel_groups(config_fpga.lvds_lanes)

    result_d = afe.get_cmd_sequence(from_history=True)

    log.info(
        f"Got AFE command sequences with {len(result_a.commands)}, {len(result_b.commands)}, {len(result_c.commands)}, {len(result_d.commands)} commands"
    )

    return result_a, result_b, result_c, result_d


def acquisition_settings(config: TPConfig) -> CommandSequence:
    tx_delays_active = list(range(len(tx_delays)))
    tx_max_delay_us = np.max(tx_delays) * 1e6
    dcdc_off_delay_us = 5 + 1.1 + tx_max_delay_us
    read_fifo_delay_us = (
        3 + config.fpga.fifo_depth / fpga.afe_clk * 1e6 - dcdc_off_delay_us
    )

    log.debug(f"{tx_max_delay_us = }")
    log.debug(f"{dcdc_off_delay_us = }")
    log.debug(f"{read_fifo_delay_us = }")

    trig_pack_id = int(
        num_packets
        - np.ceil(
            0.005 / (config.connection.packet_size * 8 / config.max_throughput_bps)
        )
    )
    if trig_pack_id < 0:
        trig_pack_id = 65535
        log.warning("Time between shots is too short to enable AFE/LVDS power down")

    result = CommandSequence(
        [
            ControlPower(domain_id=1, enable=True),  # HV+
            ControlPower(domain_id=2, enable=True),  # HV-
            ControlPower(domain_id=3, enable=True),  # - 5
            SwitchSpiMux(mux_code=1),  # FPGA
            ControlPower(domain_id=0, enable=True),  # Enable LVDS IO bank
            WriteFPGAReg(addr=10, val=16),  # Disable AFE global Power Down
            SleepMs(delay=4),
        ]
    )
    if len(tx_delays_active) == 1:
        result.add_command([SwitchSpiMux(mux_code=3)])  # TX
        tx.set_delay_prof_id(dp_id=tx_delays_active[0])
        result.add_command(tx.get_cmd_sequence(from_history=True))
        tx.load_profile()
        result.add_command(tx.get_cmd_sequence())
        result.add_command([SwitchSpiMux(mux_code=1)])  # FPGA
        for shot in range(config.num_frames):
            result.add_command(
                [
                    TriggerShot(
                        n_shots=config.fpga.num_shots,
                        n_packets=num_packets,
                        dc_dc_off_delay_us=int(dcdc_off_delay_us),
                        read_fifo_delay_us=int(read_fifo_delay_us),
                    )
                ]
            )
    else:
        for shot in range(config.num_frames):
            for id in tx_delays_active:
                result.add_command([SwitchSpiMux(mux_code=3)])  # TX
                tx.set_delay_prof_id(dp_id=tx_delays_active[0])
                result.add_command(tx.get_cmd_sequence(from_history=True))
                tx.load_profile()
                result.add_command(tx.get_cmd_sequence())
                result.add_command([SwitchSpiMux(mux_code=1)])  # FPGA
                if config.shot_delay_ms >= 0:
                    trig_pack_id = 65534
                result.add_command(
                    [
                        TriggerShot(
                            n_shots=config.fpga.num_shots,
                            n_packets=num_packets,
                            dc_dc_off_delay_us=int(dcdc_off_delay_us),
                            read_fifo_delay_us=int(read_fifo_delay_us),
                            trig_pack_id=trig_pack_id,
                        )
                    ]
                )
                if config.shot_delay_ms > 0:
                    result.add_command(SleepMs(delay=config.shot_delay_ms))
                    result.add_command(
                        ControlPower(domain_id=0, enable=True)
                    )  # Enable 2.5 V LVDS
                    result.add_command(
                        WriteFPGAReg(addr=10, val=16)
                    )  # Disable AFE Power Down
                    result.add_command(SleepMs(delay=5))

    result.add_command(
        [
            ControlPower(domain_id=0, enable=False),  # Disable LVDS IO bank
            WriteFPGAReg(addr=10, val=48),  # Enable AFE global Power Down
            ControlPower(domain_id=1, enable=False),  # HV+
            ControlPower(domain_id=2, enable=False),  # HV-
            ControlPower(domain_id=3, enable=False),  # -5V
        ]
    )

    trigger_shot_cmds: list[TriggerShot] = list(
        filter(lambda cmd: isinstance(cmd, TriggerShot), result.commands)
    )  # type: ignore
    log.info(
        f"Number of shots to be triggered: {sum(cmd.n_shots for cmd in trigger_shot_cmds)}"
    )

    log.info(f"Got acquisition command sequence with {len(result.commands)} commands")

    return result
