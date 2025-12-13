from typing import Optional

from pydantic import BaseModel


class TPConnectionConfig(BaseModel):
    mode: str
    ip: str
    packet_size: int


class TPFPGAConfig(BaseModel):
    lvds_lanes: list[int]
    fifo_depth: int
    shot_period_ms: int
    num_shots: int
    afe_clk_hispeed: bool
    txbf_clk_hispeed: bool = True
    fpga_clk_hispeed: bool = False
    afe_startcapt_delay_us: int = 0
    mcu_interrupt_src: str = "tx_bf_sync"


class TPTXStrategyConfig(BaseModel):
    name: str
    num_planewaves: int
    max_angle: float

    def as_tuple(self) -> tuple[str, int, float]:
        return (self.name, self.num_planewaves, self.max_angle)


class TPTXConfig(BaseModel):
    pulse_freq_hz: float
    num_elems: int
    pitch_m: float
    strategy: TPTXStrategyConfig
    num_pulses: int
    speed_of_sound_m_s: float = 1000


class TPAFETGCConfig(BaseModel):
    slope_db_per_us: float
    start_db: float
    stop_db: float


class TPAFEConfig(BaseModel):
    fixed_gain_atten: float
    tgc: TPAFETGCConfig
    lna_gain_db: float
    pga_gain_db: float
    lpf_freq_mhz: float
    hpf_freq_khz: float
    test_pattern: str = "normal"
    configure_tgc: bool = True
    configure_lowpower: bool = True


class TPConfig(BaseModel):
    connection: TPConnectionConfig
    fpga: TPFPGAConfig
    tx: TPTXConfig
    afe: TPAFEConfig
    num_frames: int
    max_throughput_bps: float = 32400000
    shot_delay_ms: int = 0


class TPVisualizationPreprocessMedianFilterConfig(BaseModel):
    enabled: bool
    kernel_size: int


class TPVisualizationPreprocessConfig(BaseModel):
    f_pass_frac: tuple[float, float]
    gain_stop_db: float
    median_filter_samples: Optional[int] = None
    flatten_samples: Optional[int] = None


class TPVisualizationBeamformConfig(BaseModel):
    x_range_cm: tuple[float, float]
    z_range_cm: tuple[float, float]
    resolution_px: tuple[int, int]
    db_range: int
    fov_deg: int
    correction_shift_us: float
    scaling: float = 10.0
    indexes: tuple[int, int] = (0, -1)


class TPVisualizationConfig(BaseModel):
    config: str
    rx_mapping: str
    preprocess: TPVisualizationPreprocessConfig
    beamform: TPVisualizationBeamformConfig


def main(config: str) -> None:
    with open(config, "r") as f:
        json_str = f.read()

    cfg = TPConfig.model_validate_json(json_str)

    print(cfg.model_dump_json(indent=4))


if __name__ == "__main__":
    main("config.json")
