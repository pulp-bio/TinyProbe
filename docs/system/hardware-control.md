# Hardware And Control Overview

The MCU owns the low-speed control plane. It receives host commands over Wi-Fi,
selects the correct SPI destination, controls board power domains, and reads
captured FPGA data for UDP streaming.

## SPI Multiplexing

Firmware exposes four SPI mux selections in `tp_mux_t`:

| Firmware target | Enum value | `TP_MUX_GPIO_EXTINT` | `TP_MUX_GPIO_AFETX` | Use |
| --- | --- | --- | --- | --- |
| PLL | `TP_MUX_PLL` / `0b00` | Low | Low | Low-speed PLL mux state defined by the board control path. |
| FPGA | `TP_MUX_FPGA` / `0b01` | Low | High | MCU talks to the internal FPGA SPI slave. |
| AFE | `TP_MUX_AFE` / `0b10` | High | Low | MCU SPI is forwarded to the AFE SPI chip select. |
| TX | `TP_MUX_TX` / `0b11` | High | High | MCU SPI is forwarded to the TX SPI chip select. |

## MCU To FPGA

When the mux selects `TP_MUX_FPGA`, the MCU talks to the FPGA SPI slave. The
firmware driver uses these command bytes:

| Command | Value | Purpose |
| --- | --- | --- |
| `SPI_READ_CFG` | `1` | Read the FPGA SPI configuration byte. |
| `SPI_WRITE_CFG` | `2` | Write the FPGA SPI configuration byte. |
| `SP_RD_FIFO` | `16` | Read data from the FPGA FIFO path. |
| `SPI_WR_FIFO` | `17` | Write command/control words into the FPGA SPI slave. |

FPGA register access is layered on top of `SPI_WR_FIFO`. A register write sends
the memory-controller write command, the register address, and the 32-bit value.
`tp_fpga_write_reg_safe()` writes the value, sends a NOP, reads the FIFO path,
issues a read-register command, reads the value back, and compares it.

The firmware also uses system-controller command values through register address
0: start acquisition, reset the multififo, enable readout, and echo. Trigger
shot handling resets the FPGA multififo, optionally sends start, waits for the
configured FPGA interrupt source, enables readout, then reads FIFO packets.

## FPGA To AFE And TX

The FPGA communicates with AFE and TX in two ways:

| Path | Direction | Purpose |
| --- | --- | --- |
| Forwarded SPI | MCU through FPGA pins to AFE/TX | Programs AFE and TX registers. |
| AFE clock | FPGA to AFE | Supplies the receive sampling clock when enabled. |
| AFE TX trigger | FPGA to AFE | Aligns receive-side behavior with the TX event. |
| AFE LVDS | AFE to FPGA | Carries receive data, frame clock, and bit clock. |
| TGC pins | FPGA to AFE | Drives TGC slope and direction. |
| AFE fast powerdown | FPGA to AFE | Duty-cycles AFE fast powerdown around the acquisition window. |
| TX BF clock | FPGA to TX | Supplies the TX beamformer clock when enabled. |
| TX BF sync | FPGA to TX | Triggers the TX timing profile. |
| TX TR_EN | FPGA to TX | Enables the transmit/receive switch path and periodic refresh behavior. |

## Programming AFE And TX

Programming an external analog device follows the same pattern:

1. Select `TP_MUX_AFE` or `TP_MUX_TX` in firmware.
2. Run the device-specific SPI initialization or register writes.
3. Select `TP_MUX_FPGA` again before FPGA register access or FIFO readout.
4. Start acquisition only after FPGA, AFE, TX, and power-domain state are
   coherent for the requested modality.

The startup flow in `tp_init()` follows this structure: reset FPGA, select FPGA
and configure defaults, enable board power domains, reset AFE/TX through FPGA
control, select TX and initialize it, select AFE and initialize it, then return
to the FPGA target before starting Wi-Fi command handling.

## MCU Power Responsibilities

The firmware power driver declares these TinyProbe power domains:

| Domain | Purpose |
| --- | --- |
| `TP_POWER_DOMAIN_LVDS_2_5V` | LVDS IO supply switch. |
| `TP_POWER_DOMAIN_POS_HV` | Positive high-voltage transmit rail. |
| `TP_POWER_DOMAIN_NEG_HV` | Negative high-voltage transmit rail. |
| `TP_POWER_DOMAIN_NEG_5V` | Negative 5 V analog rail. |
| `TP_POWER_DOMAIN_PLL_PWD` | Declared PLL power-down domain; currently logs not implemented in the firmware driver. |

Host acquisition flows use MCU control methods to turn these domains on before
shots and back off after acquisition. Some FPGA-controlled signals, such as AFE
fast powerdown and TX `TR_EN`, are timing signals rather than MCU GPIO power
domains.
