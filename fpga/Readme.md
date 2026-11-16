# TinyProbe FPGA project

FPGA RTL for the TinyProbe wearable ultrasound system. The FPGA controls transmitter and analog front-end (AFE) timing, receives digitized samples over LVDS, accumulates repeated acquisitions, computes averages, and returns results to the microcontroller over dual SPI.

This repository contains RTL, constraints, simulation tests, and a UDP debugging tool. MCU firmware and TiPy host software are separate projects and must match the gateware's register definitions and SPI protocol.

**Work in progress.** The included SiWG917 firmware uses the legacy single-SPI protocol and cannot operate this dual-SPI gateware. Programming both as-is does not give a working acquisition system. See the [branch release status](../README.md#fpga-release-status-work-in-progress) for scope, bandwidth limits, and remaining integration work.

## Hardware and toolchain

| Item | Current configuration |
| --- | --- |
| FPGA | Microchip IGLOO2; Libero device identifier `PA4MGL5000_N`, package `vf400` |
| Top module | `tiny_probe_top` in `sources/common/tiny_probe_top_v2.sv` |
| Generated project | `Projects/tiny_probe/tiny_probe.prjx` under `fpga/` |
| Libero | SoC 2026.1 (2026.1.0.17) |
| AFE link | AFE IC, 10-bit, 10X serialization, 1X lanes: 600 Mbps per lane, DCLK 300 MHz, FCLK 30 MHz (60 MHz ADC clock from `Clock_gen`) |
| Control clock | Fixed 10 MHz; register 1 bit 2 is reserved |
| FPGA SPI clock | 1 MHz configured in firmware for bring-up, 10 MHz interface limit |
| Simulation | Just, Python/Cocotb, QuestaSim |

## Repository structure

```text
sources/
  common/                    Board top, AFE wrapper, waveform timing, SPI routing
  dual_spi/                  dual SPI slave, transport, CDC mailboxes, stream FIFO wrapper
  rf_data_fifo/              Accumulation, averaging, FIFO wrappers, capture diagnostics
  registers/                 Configuration register bank and defaults
  ti_afe_lvds_rx/             LVDS deserialization and frame alignment
  ti_afe_tgc/                 Time-gain compensation generator
project/
  constraint/               Pins, input delays and timing constraints
tests/                      Cocotb and standalone SystemVerilog tests
tools/                      Host-side UDP acquisition debugger
```

Hog generates vendor cores from `fpga/Top/tiny_probe/post-creation.tcl`.

### Board integration and clock domains

`tiny_probe_top_v2.sv` connects board pins, differential buffers, clock components, acquisition processing, waveform controls, and MCU transport. `EXT_OSC` and `Clock_gen` generate internal clocks from the board reference. AFE bit/frame clocks, waveform/core timing, result readout, and SPI SCLK form separate clock domains.

Capture controls are synchronized into the AFE frame-clock domain. Asynchronous result FIFOs transfer sample data, while `tp_req_ack_mailbox.sv` transfers register requests and responses across SPI/core domains. `async_sym_fifo_sf2.sv` converts the project's active-high FIFO reset to the generated CoreFIFO's active-low reset.

`spi_demux.sv` routes external MCU SPI access to the AFE or transmitter. The FPGA also supplies clock enables, resets, powerdown controls, trigger/interrupt outputs, and TGC slope/direction signals through the `ti_afe_tgc` submodule.

### Acquisition datapath

1. `afe_rx.sv` wraps the LVDS receiver submodule to deserialize and align each lane's 20-bit frame.
2. `waveform_generator_fsm.sv` generates sequence, shot, and capture controls, using `waveform_gen.sv` for internal timing.
3. `accumulation.sv` stores the first shot in per-lane FIFOs. Later shots read, add, and write corresponding sample positions.
4. Signed 10-bit samples are converted to offset-binary values for unsigned accumulation. Averaging removes the bias afterwards.
5. After the final shot, `result_average_engine.sv` processes enabled lanes and shares `sample_average_divider.sv` between samples.
6. Averaged samples enter asynchronous result FIFOs for readout by the SPI transport.

The board top currently uses 13 bits per accumulated sample, making a 26-bit accumulation frame. The generated RF FIFO has 26-bit words and 1024 entries. Although the shot-count register is eight bits wide, supported counts also depend on accumulator capacity: 13 bits can represent the worst-case sum of eight offset-binary 10-bit samples. Larger counts require reviewing RTL widths and generated FIFO configuration.

### SPI result transport

`tinyprobe_qspi_transport.sv` combines the SPI slave, registers, CDC mailboxes, acquisition start/reset controls, lane reader, byte packing, stream FIFO, and diagnostics. The board enables dual-data operation despite the historical `quad` and `QSPI` module names.

The current `multi_fifo_reader.sv` emits 1000 bytes per enabled lane. When a lane empties, it preserves any partial byte and pads the remaining bytes with zeros. It stops at the byte limit even if FIFO words remain; acquisition reset clears surplus data before the next sequence.

| Opcode | Operation |
| --- | --- |
| `0x32` | Register write |
| `0x4C` | Register readback |
| `0x6B` | Acquisition stream read |

The controller uses SPI mode 1 (`CPOL=0`, `CPHA=1`), command/address phases, and ten dummy SCLK cycles for reads. MCU firmware must match the data-lane mode and response boundary. See `sources/dual_spi/spi_quad_controller.sv` and `spi_quad_shift_reg.sv` for transaction details.

## Acquisition modes

| Mode | Start behavior | Output behavior |
| --- | --- | --- |
| US | MCU starts an internally timed sequence | Ultrasound timing, repeated for the configured shot count |
| OA | MCU starts an internally timed sequence | OA pulse timing; physical TX `TR_EN` remains low |
| OA_EXTERNAL | MCU arms the receiver | Accepted external rising edges start captures; A19 excitation and TX `TR_EN` remain low|

All modes share accumulation, averaging, and readout. Register 12 bit 24 selects OA, and bit 25 selects external sequencing. Configure the mode before starting acquisition.

The documented external input is F15, LVCMOS18, active-high. High and low levels must each last at least 50 ns. Synchronization and configured capture delay add latency; this is not pre-trigger capture.

## Registers and diagnostics

The transport exposes sixteen 32-bit registers. This table summarizes the board-top connections; use the RTL and matching MCU/TiPy register map for exact field semantics and timing units.

| Register | Purpose |
| --- | --- |
| 0 | Transport command handling; see `tinyprobe_qspi_transport.sv` |
| 1 | PLL/clock controls; bits 23:8 also supply OA pulse-width configuration |
| 2 | Lane enables in bits 15:0, frame count in bits 27:16, clock-buffer overrides |
| 3 | Sequence period and TX wake/sleep timing |
| 4 | AFE wake and clock-on timing |
| 5 | Capture delay and AFE acquisition timing |
| 6–9 | TGC clock division, capture duration, and start/finish delays |
| 10 | AFE/TX reset and manual power/output overrides |
| 11 | Capture-start timing; shot count in bits 7:0, with zero treated as one |
| 12 | TX refresh settings; OA bit 24 and external-mode bit 25 |
| 13 | Trigger/interrupt routing and diagnostic selection |
| 14–15 | Status/readback; register 15 includes selected diagnostic pages |

An optional diagnostic trace records up to 16 lane-0 entries at the shot, accumulation, and averaging stages. Register 13 bit 23 enables capture; diagnostic register readback exposes the records.

## Build

Use Git Bash with the following prerequisites.

- Libero SoC 2026.1.0.17 with `Designer/bin` on `PATH` and the licence in `LM_LICENSE_FILE`.
- Tcllib 2.0 with `HOG_TCLLIB_PATH` pointing to its `modules` directory.
- Libero Vault cores FCCC 2.0.201, OSC 2.0.101, and COREFIFO 2.8.101.

Initialize submodules once after cloning, from the repository root.

```bash
git submodule update --init --recursive
```

Build from `fpga/`.

```bash
./Hog/Do WORKFLOW tiny_probe -recreate
```

Open the generated project at `Projects/tiny_probe/tiny_probe.prjx`. Check the setup and hold reports under `bin/`.

The pinned Hog revision includes Libero fixes and supports version tracking with the build rooted in `fpga/`.

## AFE capture timing (600 Mbps)

The AFE receiver (`afe_rx`, `ti_afe_lvds_rx`) captures each data lane with an I/O DDR register on the AFE bit clock (DCLK) and samples the 20-bit frame on the frame clock (FCLK). Its timing closure needs these project settings together:

| Setting | File | Value |
| --- | --- | --- |
| Clocks and AFE input window | `constraint/timing_constraints.sdc` | DCLK 3.333 ns, FCLK 33.333 ns; input delay min UI/2 − 0.4 ns and max UI/2 + 0.4 ns on both DCLK edges; provisional 0.4 ns DCLK-to-FCLK uncertainty |
| FPGA input delay taps | `constraint/io/phys_constr_gen_v2_igloo.pdc` | `-IN_DELAY 17` on both pins of lanes 1 and 3, `18` on all other data lanes, `0` on DCLK and FCLK |
| Placement | `fpga/Top/tiny_probe/hog.conf` | High effort, timing-driven placement and hold repair|
| Operating conditions | `fpga/Top/tiny_probe/post-creation.tcl` | FPGA junction 10/25/60 °C, all process corners, core 1.14 to 1.26 V |


Check setup and hold reports in `fpga/bin/tiny_probe-<version>/` after each build.



## Troubleshooting Libero

### Undefined or missing components

If synthesis reports an undefined module such as `Clock_gen`, right-click the component in **Design Hierarchy** and select **Generate Component**.

If the component has a question mark or cannot be generated, use **File > Import** to import its component definition. For `Clock_gen`, select:

```text
Projects\tiny_probe\component\work\Clock_gen\Clock_gen.cxf
```

Repeat the import/generation procedure for other missing components using their corresponding `.cxf` files.

### COREFIFO version or port mismatch

This project requires **COREFIFO 2.8.101**. If Design Hierarchy shows a different version, right-click the component, select **Update Component Version**, and choose **2.8.101**. If the mismatch persists, switching to another version and then back to **2.8.101** may resolve it. Regenerate the component afterwards.

### Unexpected signals or component interfaces

Check the source path of the component Libero is using; it must be under `Projects\tiny_probe\component\work`. Older plain-HDL copies of `Clock_gen` and `RF_DATA_FIFO` from Libero v12.6 used to sit in `project\hdl`; the `RF_DATA_FIFO` copy lacks the `DVLD` port ("Port DVLD does not exist"). They were removed, so if such a copy reappears, delete it and regenerate the component.

### Missing FIFO simulation files

The generated FIFO HDL is under:

```text
Projects\tiny_probe\component\work\RF_DATA_FIFO\RF_DATA_FIFO_0\rtl\vlog\core
```

and the generated FIFO testbench under `Projects\tiny_probe\component\work\RF_DATA_FIFO\RF_DATA_FIFO_0\rtl\vlog\test\user`. Ensure the simulation configuration points to these files.


## Simulation and tests

See [FPGA test instructions](tests/README.md).


## License

Project-owned FPGA sources and build recipes use the [Solderpad Hardware License Version 0.51](../licenses/LICENSE.hw). Hog and locally generated vendor IP retain their own licenses.
