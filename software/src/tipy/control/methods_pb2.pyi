from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Powerdomain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LVDS_2V5: _ClassVar[Powerdomain]
    POS_HV: _ClassVar[Powerdomain]
    NEG_HV: _ClassVar[Powerdomain]
    NEG_5V: _ClassVar[Powerdomain]
    PLL_PWD: _ClassVar[Powerdomain]

class Spidomain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLL: _ClassVar[Spidomain]
    FPGA: _ClassVar[Spidomain]
    AFE: _ClassVar[Spidomain]
    TX: _ClassVar[Spidomain]

class Loglevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRACE: _ClassVar[Loglevel]
    DEBUG: _ClassVar[Loglevel]
    INFO: _ClassVar[Loglevel]
    WARN: _ClassVar[Loglevel]
    ERROR: _ClassVar[Loglevel]
    FATAL: _ClassVar[Loglevel]

class status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[status]
    INVALID_ARGUMENT: _ClassVar[status]
    INVALID_STATE: _ClassVar[status]
    TIMEOUT: _ClassVar[status]
    UNKNOWN_ERROR: _ClassVar[status]
LVDS_2V5: Powerdomain
POS_HV: Powerdomain
NEG_HV: Powerdomain
NEG_5V: Powerdomain
PLL_PWD: Powerdomain
PLL: Spidomain
FPGA: Spidomain
AFE: Spidomain
TX: Spidomain
TRACE: Loglevel
DEBUG: Loglevel
INFO: Loglevel
WARN: Loglevel
ERROR: Loglevel
FATAL: Loglevel
OK: status
INVALID_ARGUMENT: status
INVALID_STATE: status
TIMEOUT: status
UNKNOWN_ERROR: status

class controlpower_args(_message.Message):
    __slots__ = ("domain", "enable")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    domain: Powerdomain
    enable: bool
    def __init__(self, domain: _Optional[_Union[Powerdomain, str]] = ..., enable: _Optional[bool] = ...) -> None: ...

class controlspi_args(_message.Message):
    __slots__ = ("domain",)
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    domain: Spidomain
    def __init__(self, domain: _Optional[_Union[Spidomain, str]] = ...) -> None: ...

class delayms_args(_message.Message):
    __slots__ = ("delay",)
    DELAY_FIELD_NUMBER: _ClassVar[int]
    delay: int
    def __init__(self, delay: _Optional[int] = ...) -> None: ...

class delayns_args(_message.Message):
    __slots__ = ("delay",)
    DELAY_FIELD_NUMBER: _ClassVar[int]
    delay: int
    def __init__(self, delay: _Optional[int] = ...) -> None: ...

class loop_args(_message.Message):
    __slots__ = ("iterations", "command_index")
    ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    COMMAND_INDEX_FIELD_NUMBER: _ClassVar[int]
    iterations: int
    command_index: int
    def __init__(self, iterations: _Optional[int] = ..., command_index: _Optional[int] = ...) -> None: ...

class ping_args(_message.Message):
    __slots__ = ("probe_id",)
    PROBE_ID_FIELD_NUMBER: _ClassVar[int]
    probe_id: int
    def __init__(self, probe_id: _Optional[int] = ...) -> None: ...

class setloglevel_args(_message.Message):
    __slots__ = ("level",)
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    level: Loglevel
    def __init__(self, level: _Optional[_Union[Loglevel, str]] = ...) -> None: ...

class triggershot_args(_message.Message):
    __slots__ = ("num_shots", "num_packets", "delay_dcdc_off_ns", "delay_read_fifo_ns", "callback_id", "software_trigger", "pwd_dcdc_at_rx")
    NUM_SHOTS_FIELD_NUMBER: _ClassVar[int]
    NUM_PACKETS_FIELD_NUMBER: _ClassVar[int]
    DELAY_DCDC_OFF_NS_FIELD_NUMBER: _ClassVar[int]
    DELAY_READ_FIFO_NS_FIELD_NUMBER: _ClassVar[int]
    CALLBACK_ID_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    PWD_DCDC_AT_RX_FIELD_NUMBER: _ClassVar[int]
    num_shots: int
    num_packets: int
    delay_dcdc_off_ns: int
    delay_read_fifo_ns: int
    callback_id: int
    software_trigger: bool
    pwd_dcdc_at_rx: bool
    def __init__(self, num_shots: _Optional[int] = ..., num_packets: _Optional[int] = ..., delay_dcdc_off_ns: _Optional[int] = ..., delay_read_fifo_ns: _Optional[int] = ..., callback_id: _Optional[int] = ..., software_trigger: _Optional[bool] = ..., pwd_dcdc_at_rx: _Optional[bool] = ...) -> None: ...

class writeafe_args(_message.Message):
    __slots__ = ("dtgc", "address", "value")
    DTGC_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    dtgc: bool
    address: int
    value: int
    def __init__(self, dtgc: _Optional[bool] = ..., address: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

class writefpga_args(_message.Message):
    __slots__ = ("address", "value")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    address: int
    value: int
    def __init__(self, address: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

class writetx_args(_message.Message):
    __slots__ = ("address", "value")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    address: int
    value: int
    def __init__(self, address: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

class cmd(_message.Message):
    __slots__ = ("controlpower", "controlspi", "delayms", "delayns", "loop", "ping", "setloglevel", "triggershot", "writeafe", "writefpga", "writetx")
    CONTROLPOWER_FIELD_NUMBER: _ClassVar[int]
    CONTROLSPI_FIELD_NUMBER: _ClassVar[int]
    DELAYMS_FIELD_NUMBER: _ClassVar[int]
    DELAYNS_FIELD_NUMBER: _ClassVar[int]
    LOOP_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    SETLOGLEVEL_FIELD_NUMBER: _ClassVar[int]
    TRIGGERSHOT_FIELD_NUMBER: _ClassVar[int]
    WRITEAFE_FIELD_NUMBER: _ClassVar[int]
    WRITEFPGA_FIELD_NUMBER: _ClassVar[int]
    WRITETX_FIELD_NUMBER: _ClassVar[int]
    controlpower: controlpower_args
    controlspi: controlspi_args
    delayms: delayms_args
    delayns: delayns_args
    loop: loop_args
    ping: ping_args
    setloglevel: setloglevel_args
    triggershot: triggershot_args
    writeafe: writeafe_args
    writefpga: writefpga_args
    writetx: writetx_args
    def __init__(self, controlpower: _Optional[_Union[controlpower_args, _Mapping]] = ..., controlspi: _Optional[_Union[controlspi_args, _Mapping]] = ..., delayms: _Optional[_Union[delayms_args, _Mapping]] = ..., delayns: _Optional[_Union[delayns_args, _Mapping]] = ..., loop: _Optional[_Union[loop_args, _Mapping]] = ..., ping: _Optional[_Union[ping_args, _Mapping]] = ..., setloglevel: _Optional[_Union[setloglevel_args, _Mapping]] = ..., triggershot: _Optional[_Union[triggershot_args, _Mapping]] = ..., writeafe: _Optional[_Union[writeafe_args, _Mapping]] = ..., writefpga: _Optional[_Union[writefpga_args, _Mapping]] = ..., writetx: _Optional[_Union[writetx_args, _Mapping]] = ...) -> None: ...

class request(_message.Message):
    __slots__ = ("cmd",)
    CMD_FIELD_NUMBER: _ClassVar[int]
    cmd: _containers.RepeatedCompositeFieldContainer[cmd]
    def __init__(self, cmd: _Optional[_Iterable[_Union[cmd, _Mapping]]] = ...) -> None: ...

class response(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _containers.RepeatedScalarFieldContainer[status]
    def __init__(self, status: _Optional[_Iterable[_Union[status, str]]] = ...) -> None: ...
