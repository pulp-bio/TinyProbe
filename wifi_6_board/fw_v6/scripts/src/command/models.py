from dataclasses import dataclass

from .command import Command


@dataclass
class PingCommand(Command):
    _id: int = 0
    _format: str = "B"

    probe_id: int = 1


@dataclass
class ActivateReplies(Command):
    _id: int = 1
    _format: str = "B"

    replies_on: int = 1


@dataclass
class SwitchSpiMux(Command):
    _id: int = 2
    _format: str = "B"

    mux_code: int = 0


@dataclass
class WriteSpiPacket(Command):
    _id: int = 3
    _format: str = "s"

    bytes_array: bytes = b""


@dataclass
class WriteFPGAReg(Command):
    _id: int = 4
    _format: str = "BI"

    addr: int = 0
    val: int = 0


@dataclass
class WriteAfeReg(Command):
    _id: int = 5
    _format: str = "BBH"

    dtgc_die: bool = False
    addr: int = 0
    val: int = 0


@dataclass
class WriteTxReg(Command):
    _id: int = 6
    _format: str = "HI"

    addr: int = 0
    val: int = 0


@dataclass
class DelayNs(Command):
    _id: int = 7
    _format: str = "Q"

    delay: int = 0


@dataclass
class SleepMs(Command):
    _id: int = 8
    _format: str = "I"

    delay: int = 0


@dataclass
class ControlPower(Command):
    _id: int = 9
    _format: str = "BB"

    domain_id: int = 0
    enable: bool = False


@dataclass
class TriggerShot(Command):
    _id: int = 10
    _format: str = "HHBBHBB"

    n_shots: int = 1
    n_packets: int = 82
    dc_dc_off_delay_us: int = 61  # in 0.1us
    read_fifo_delay_us: int = 200
    trig_pack_id: int = 65535
    sw_trigger: bool = True
    dc_dc_pwd_at_rx: bool = True


@dataclass
class SetPowersaveMode(Command):
    _id: int = 11
    _format: str = "BB"

    domain: int = 0
    enable: bool = False
