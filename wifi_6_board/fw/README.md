# WiUS (Wireless Ultrasound) Firmware - TinyProbe WiFi v2

## Requisites

In order to use this firmware, you need to install Simplicity Studio. To get an introduction, check the [Toolchain Getting Started][toolchain_getting_started] guide.

Additionally, make sure you have the following tools installed on your system:
- Python 3.7 or higher (We suggest using [uv](https://docs.astral.sh/uv/))
- Make (We will use the Makefile to build and flash the project)

## Build and Flash Instructions

**Note:** These instructions assume you have made your way through the [Toolchain Getting Started][toolchain_getting_started] guide and have set up the example project as described there.

In order to build and flash the firmware, we will simply use the provided Makefile. This way, we circumvent the need to use Simplicity Studio directly, which does not work well on some systems.

Thus, open this directory in a terminal and run:

```bash
make
```

### Environment Variables

You will see the following error:

```bash
make: *** No rule to make target '.env', needed by 'user/env.h'.  Stop.
```

This project includes some sensitive information that is included at build time and that should not be committed to version control. To proceed, you need to provide this information in a safe(ish) way.

The project expects Wi-Fi credentials:

- `WIUS_WIFI_SSID`: Wi-Fi network name
- `WIUS_WIFI_PASS`: Wi-Fi password

Provide them in one of two ways:

- `env.h` in the user directory:
  
  ```c
  #ifndef ENV_H
  #define ENV_H

  #define WIUS_WIFI_SSID "<your_wifi_ssid>"
  #define WIUS_WIFI_PASS "<your_wifi_password>"

  #endif /* ENV_H */

  ```

- `.env` file in this directory:
  
  ```bash
  WIUS_WIFI_SSID=<your_wifi_ssid>
  WIUS_WIFI_PASS=<your_wifi_password>
  ```

  Which will be used to generate `user/env.h` at build time.

### Building

Now, run again:

```bash
make
```

This should build the project without errors. The resulting firmware binary will be located at `cmake_gcc/build/base/fw_v6.hex`.

### Flashing

To flash the firmware to the device, connect it via USB and run:

```bash
make flash
```

**Note:** On Linux, you need to install the udev rules for the board to be recognized. Please refer to the [Toolchain Getting Started][toolchain_getting_started] guide for more information.

### Monitoring

To monitor the logging output of the device, we need to attach via RTT. This is also included in the Makefile two ways:

```make
make attach       # Attach without resetting the device
make attach_reset # Attach with a device reset
```

## Code Structure

The code is structured to be modular and easy to understand. All of the code which is written by us is in the `user` directory. The code is divided into the following directories:
- `user/wius`: Low-level and Hardware-specific code for the WiUS PCB
  - Peripheral drivers
  - Networking drivers
  - etc.
- `user/tp`: TinyProbe-specific code built on top of the WiUS code
  - Power Management
  - AFE/TX drivers
  - Command handlers
  - etc.
- Other, common code that is used by both WiUS and TinyProbe
  - user.h / user.c: User entry point for the firmware
  - log.h / log.c: Logging code
  - common.h / common.c: Common code that is used by both WiUS and TinyProbe
  - config.h: Constants and configuration code

Any scripts used for development are located in the `scripts` directory. Refer to the [scripts overview][scripts_overview] for more information.

For detailed architecture documentation, see the generated Doxygen documentation (_Firmware Structure_).

## Licensing

WiSeConnect 3 SDK is covered by one of several different licenses. The default license is the [Master Software License Agreement](https://www.silabs.com/about-us/legal/master-software-license-agreement) (MSLA), which applies unless otherwise noted. See [LICENSE.md](LICENSE.md) for full details.

This project in particular also uses code from the [FreeRTOS](https://github.com/FreeRTOS) project, which is licensed under the [MIT License](https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/LICENSE.md), as well as code from the [CMSIS library](https://github.com/ARM-software/CMSIS_6), which is licensed under the [Apache License 2.0](https://github.com/ARM-software/CMSIS_6/blob/main/LICENSE).


The code developed at [Integrated Systems Laboratory (IIS)](https://iis.ee.ethz.ch/) (ETH Zurich) is licensed under the Apache License 2.0.

[toolchain_getting_started]: docs/toolchain.md
[scripts_overview]: scripts/overview.md
