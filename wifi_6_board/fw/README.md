# WiUS (Wireless Ultrasound) Firmware - TinyProbe WiFi v2

## Requisites

In order to use this firmware, you need to install Simplicity Studio. To get an introduction, check the [Toolchain Getting Started](docs/toolchain.md) guide.

## Build and Flash Instructions

Please follow the instructions in the [Toolchain Getting Started](docs/toolchain.md) guide for detailed steps on building and flashing the firmware.

### Environment Variables

The project expects Wi-Fi credentials:

- `WIUS_WIFI_SSID`: Wi-Fi network name
- `WIUS_WIFI_PASS`: Wi-Fi password

Provide them in one of two ways:

- `env.h` in the repo root:
  ```c
  #ifndef ENV_H
  #define ENV_H

  #define WIUS_WIFI_SSID "<your_wifi_ssid>"
  #define WIUS_WIFI_PASS "<your_wifi_password>"

  #endif /* ENV_H */
  ```

- `.env` file in the repo root:
  ```bash
  WIUS_WIFI_SSID=<your_wifi_ssid>
  WIUS_WIFI_PASS=<your_wifi_password>
  ```
  Then generate env.h via:
  ```powershell
  python scripts/fetch_env.py .env env.h
  ```
  or `make user/env.h`.

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

For detailed architecture documentation, see the generated Doxygen documentation.

## Licensing

WiSeConnect 3 SDK is covered by one of several different licenses. The default license is the [Master Software License Agreement](https://www.silabs.com/about-us/legal/master-software-license-agreement) (MSLA), which applies unless otherwise noted. See [LICENSE.md](LICENSE.md) for full details.

This project in particular also uses code from the [FreeRTOS](https://github.com/FreeRTOS) project, which is licensed under the [MIT License](https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/LICENSE.md), as well as code from the [CMSIS library](https://github.com/ARM-software/CMSIS_6), which is licensed under the [Apache License 2.0](https://github.com/ARM-software/CMSIS_6/blob/main/LICENSE).


The code developed at [Integrated Systems Laboratory (IIS)](https://iis.ee.ethz.ch/) (ETH Zurich) is licensed under the Apache License 2.0.
