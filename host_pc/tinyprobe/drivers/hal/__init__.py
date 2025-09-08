from tinyprobe.drivers.ll.fpga_ll import TP_LL_FPGA
from tinyprobe.drivers.ll.afe5832lp_ll import TP_LL_AFE5832LP_GLB, TP_LL_AFE5832LP_DTGC
from tinyprobe.drivers.ll.tx7332_ll import TP_LL_TX7332

DRIVERS_HAL = {
    "FPGA": TP_LL_FPGA,
    "AFE5832LP": [TP_LL_AFE5832LP_GLB, TP_LL_AFE5832LP_DTGC],
    "TX7332": TP_LL_TX7332,
}


class TP_HAL(object):
    def __init__(self, name: str):
        self._name = name

        if name not in DRIVERS_HAL:
            raise ValueError(f"Unknown driver: {name}")

    def __str__(self):
        return self._name + " HAL Driver"
