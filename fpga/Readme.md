# TinyProbe FPGA project

FPGA RTL for the TinyProbe wearable ultrasound system. The FPGA controls transmitter and analog front-end (AFE) timing, receives digitized samples over LVDS, accumulates repeated acquisitions, computes averages, and returns results to the microcontroller over dual SPI.

This repository contains RTL, the Microchip Libero project, generated components, simulation tests, and a UDP debugging tool. MCU firmware and TiPy host software are separate projects and must match the gateware's register definitions and SPI protocol.

## Hardware and toolchain

| Item | Current configuration |
| --- | --- |
| FPGA | Microchip IGLOO2; Libero device identifier `PA4MGL5000_N`, package `vf400` |
| Top module | `tiny_probe_top` in `sources/common/tiny_probe_top_v2.sv` |
| Project | `project/tiny_probe.prjx` |
| Libero | 2025.1, as recorded in the project and setup report (dont use any other version!) |
| Simulation | Windows, MSYS2 Make, Python/Cocotb, QuestaSim |

The original setup used Libero 12.6. Use the current project's recorded 2025.1 version as the starting point for this checkout.

## Repository structure

```text
sources/
  common/                    Board top, AFE wrapper, waveform timing, SPI routing
  dual_spi/                  dual SPI slave, transport, CDC mailboxes, stream FIFO wrapper
  rf_data_fifo/              Accumulation, averaging, FIFO wrappers, capture diagnostics
  registers/                 Configuration registers and reset defaults
  ti_afe_lvds_rx/            Submodule: LVDS deserialization and frame alignment
  ti_afe_tgc/                Submodule: time-gain compensation generator
project/
  tiny_probe.prjx            Libero project and source/component registrations
  build_programming_data.tcl Implementation flow script
  component/                Generated clock, oscillator, and FIFO components
  hdl/                      Imported/generated HDL and local diagnostic module
  constraint/               Pin, synthesis-clock, and timing constraints
  stimulus/                 Libero simulation stimulus
MicrochipCommon/vault/       Vendor IP catalog metadata
tests/                      Cocotb and standalone SystemVerilog tests
tools/                      Host-side UDP acquisition debugger
```

`sources/` contains the main maintained RTL. Generated and imported HDL under `project/component/` and `project/hdl/` also are part in the build.

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

## Libero installation

### Requirements

- Windows machine.
- Libero SoC 2025.1.
- Access to the ETH license servers listed below.

1. Create these Windows environment variables before launching Libero:

   | Name | Value |
   | --- | --- |
   | `LM_LICENSE_FILE` | `8169@lic-synopsys-r.ethz.ch;8183@lic-microsemi.ethz.ch` |
   | `TINY_PROBE_SRC_PATH` | `D:\Workspace\TinyProbe\tiny_probe_fpga_project\sources` — replace this example with the absolute `sources` directory in your checkout |

2. Download the **Libero SoC Design Suite Version 2025.1 Full Installer** from the [Microchip FPGA software downloads page](https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga-software-downloads).
3. Run `Libero_SoC_2025.1_offline_pc.exe` as administrator to install the suite.
4. Restart Libero after setting the environment variables. Open the project using `project/tiny_probe.prjx`. If Libero closes while opening the project, relaunch it and open the project again; this has been observed with this setup.
5. Before each synthesis run, select **Build Hierarchy** in the **Design Hierarchy** window.
6. Double-click **Synthesis** in the **Design Flow** window to start synthesis.

## Clone and open the project

```powershell
git clone git@gitlab.ethz.ch:tinyprobe/tiny_probe_fpga_project.git
cd tiny_probe_fpga_project
git submodule update --init --recursive
```

Set `TINY_PROBE_SRC_PATH` to the absolute `sources` directory. From the repository root in PowerShell:

```powershell
$sourcePath = Join-Path (Get-Location).Path 'sources'
$env:TINY_PROBE_SRC_PATH = $sourcePath
[Environment]::SetEnvironmentVariable('TINY_PROBE_SRC_PATH', $sourcePath, 'User')
```

Restart Libero after setting the persistent variable and open `project/tiny_probe.prjx`. Check that linked files resolve and the active root is `tiny_probe_top::work`.

## Build and programming data

Run the Libero flow in this order:

Before starting synthesis, run **Build Hierarchy** in the **Design Hierarchy** window.

1. Synthesis.
2. Place and route.
3. Timing verification.
4. Programming-data generation.

## Troubleshooting Libero

### Undefined or missing components

If synthesis reports an undefined module such as `Clock_gen`, right-click the component in **Design Hierarchy** and select **Generate Component**.

If the component has a question mark or cannot be generated, use **File > Import** to import its component definition. For `Clock_gen`, select:

```text
project\component\work\Clock_gen\Clock_gen.cxf
```

Repeat the import/generation procedure for other missing components using their corresponding `.cxf` files.

### COREFIFO version or port mismatch

This project requires **COREFIFO 2.8.101**. If Design Hierarchy shows a different version, right-click the component, select **Update Component Version**, and choose **2.8.101**. If the mismatch persists, switching to another version and then back to **2.8.101** may resolve it. Regenerate the component afterwards.

### Unexpected signals or component interfaces

Check the source path of the component Libero is using. Imported and generated copies exist in this repository; an incorrect path can select a different implementation or interface.

### Missing FIFO simulation files

Check the imported FIFO HDL under:

```text
project\hdl\RF_DATA_FIFO_0\rtl\vlog\core
```

That directory contains FIFO implementation files. The imported FIFO testbench is under:

```text
project\hdl\RF_DATA_FIFO_0\rtl\vlog\test\user
```

Also check the corresponding generated files under `project\component\work\RF_DATA_FIFO\RF_DATA_FIFO_0` and ensure the simulation configuration points to the intended files.

## Simulation and tests

See [tests/README.md](tests/README.md) for the existing Windows/MSYS2 instructions. The Makefiles use Cocotb and default to the `questa-compat` simulator selection.

In an MSYS2 terminal, install Make and prepare Python/Cocotb. Adapt installation paths to your machine:

```bash
pacman -S --needed make
source /c/Users/oderl/anaconda3/etc/profile.d/conda.sh
conda create -n cocotb python=3.11 pip -y
conda activate cocotb
python -m pip install cocotb
export PATH="/c/Microchip/Libero_SoC_2025.1/Libero_SoC/QuestaSim_Pro/win64:$PATH"
```

