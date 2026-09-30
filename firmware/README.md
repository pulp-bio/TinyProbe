# TinyProbe Firmware

This directory contains the firmware for the SiWG917 Wi-Fi 6 MCU used in TinyProbe.


## Requisites

In order to use this firmware, you need to install Simplicity Studio. To get an introduction, check the [Toolchain Getting Started][toolchain_getting_started] guide.

Additionally, make sure you have the dependencies installed as described in the [Development section of the main README](../README.md#development).

**Note:** Using a container is the recommended way to build and flash the firmware, as it ensures a consistent development environment across different systems. See the [Containerized Development](#containerized-development) section for more information.


## Build and Flash Instructions

**Note:** These instructions assume you have made your way through the [Toolchain Getting Started][toolchain_getting_started] guide and have set up the example project as described there.

In order to build and flash the firmware, we will simply use the provided Justfile. This way, we circumvent the need to use Simplicity Studio directly, which does not work well on some systems.

From this directory, `just` lists the available recipes. To build:

```bash
just build
```


### Environment Variables

You will see the following error:

```bash
FileNotFoundError: [Errno 2] No such file or directory: '.env'
```

This project includes some sensitive information that is included at build time and that should not be committed to version control. To proceed, you need to provide this information in a safe(ish) way.

The project expects Wi-Fi credentials:

- `WIUS_WIFI_SSID`: Wi-Fi network name
- `WIUS_WIFI_PASS`: Wi-Fi password

Create a `.env` file in this directory:

```bash
WIUS_WIFI_SSID=<your_wifi_ssid>
WIUS_WIFI_PASS=<your_wifi_password>
```

`just build` generates `user/env.h` from this file. Do **not** commit `.env` or `user/env.h`.


### Building

If the CMake project files have not been generated yet (for example after a fresh clone), run:

```bash
just generate
```

Then build:

```bash
just build
```

This should build the project without errors. The resulting firmware binary will be located at `cmake_gcc/build/base/fw_v6.hex`.


### Flashing

To flash the firmware to the device, connect it via USB and run:

```bash
just flash
```

**Note:** On Linux, you need to install the udev rules for the board to be recognized. Please refer to the [Toolchain Getting Started][toolchain_getting_started] guide for more information.


### Monitoring

To monitor the logging output of the device, attach via RTT:

```bash
just attach       # Attach without resetting the device
just attach_reset # Attach with a device reset
```


### Cleaning

```bash
just clean      # Remove the CMake build directory and generated user/env.h
just clean_all  # Also remove SLC-generated files and config files except pin_config.h
```


## Code Structure

`config/pin_config.h` is a header containing the WiUS SSI and GSPI pin assignments. Keep it in source control and preserve it when cleaning or regenerating SDK configuration files. Edit board pin assignments in this header rather than replacing it with Pin Tool output.

The application code is in the `user` directory, divided into the following directories:
- `user/wius`: Low-level and Hardware-specific code for the WiUS PCB
  - Peripheral drivers
  - Networking drivers
  - etc.
- `user/tp`: TinyProbe-specific code built on top of the WiUS code
  - Power Management
  - AFE/TX drivers (pre-compiled)
  - Command handlers
  - etc.
- `user/common`: Other, common code that is used by both WiUS and TinyProbe
  - common.h / common.c: Common code that is used by both WiUS and TinyProbe
  - log.h / log.c: Logging code
  - led.h / led.c: LED control code
- `user/config.h`: Constants and configuration code
- `user/user.h`/`user/user.c`: User entry point for the firmware


## Containerized Development

A self-contained firmware toolchain is provided under [`../container/`](../container). See [that README](../container/README.md) for prerequisites (including the SLT installer zip), recipe details, and Dev Container setup.

### Docker

**Note:** Tested on Windows 11 with WSL 2.

```bash
cd ../container
just build
just run
```

### Apptainer

**Note:** Tested on ETH IIS Alma Linux clients.

```bash
cd ../container
just build_appt
just run_appt
```

From the repository root you can also use `just container run` / `just container run_appt`.

Inside the container, continue with the build steps above (`just generate`, `just build`, etc.).


## Licensing

The firmware written at the [Integrated Systems Laboratory (IIS)](https://iis.ee.ethz.ch/) (ETH Zurich) is licensed under the [Apache License 2.0](../licenses/LICENSE.sw). That is the code under `user/`, plus `main.c` and `config/pin_config.h`.

This directory does not include the Silicon Labs Simplicity SDK or the WiseConnect 3 SDK. Install them locally (see the [Toolchain Getting Started][toolchain_getting_started] guide, or use the container under `../container/`), then run `just generate`. That step writes SDK sources and generated headers such as `sl_board_configuration.h` into this tree. They are covered by the [Master Software License Agreement](https://www.silabs.com/about-us/legal/master-software-license-agreement) and the corresponding license conditions apply.

[nanopb](https://github.com/nanopb/nanopb) is vendored under `vendor/nanopb` and is licensed under the [Zlib License](https://github.com/nanopb/nanopb/blob/master/LICENSE.txt).

### AFE5832LP and TX7332 drivers

The drivers for the [AFE5832LP](user/tp/hal/tp_afe.h) and [TX7332](user/tp/hal/tp_tx.h) are included in this repository as precompiled binaries; source code for these drivers is not released as distribution restrictions apply.

[toolchain_getting_started]: ../docs/firmware/toolchain.md
