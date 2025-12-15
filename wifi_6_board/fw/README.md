# WiUS (Wireless Ultrasound) Firmware - TinyProbe WiFi v2

- [WiUS (Wireless Ultrasound) Firmware - TinyProbe WiFi v2](#wius-wireless-ultrasound-firmware---tinyprobe-wifi-v2)
  - [Requisites](#requisites)
  - [Build, Flash and Debug](#build-flash-and-debug)
    - [Opening the Project](#opening-the-project)
    - [Building the Project](#building-the-project)
      - [Environment Variables](#environment-variables)
        - [`env.h` File](#envh-file)
        - [`.env` File](#env-file)
      - [Building Setup](#building-setup)
      - [Subsequent Builds](#subsequent-builds)
    - [Flashing the Project](#flashing-the-project)
    - [Debugging the Project](#debugging-the-project)
  - [Code Structure](#code-structure)
  - [Licensing](#licensing)


## Requisites

In order to use this firmware, you need to install Simplicity Studio. You can download it from the [Silicon Labs website](https://www.silabs.com/developers/simplicity-studio).

To get an introduction to Simplicity Studio, check the [Developing with WiSeConnect™ SDK v3.x with SiWx91x™ Boards](https://docs.silabs.com/wiseconnect/latest/wiseconnect-developers-guide-developing-for-silabs-hosts/) guide.

## Build, Flash and Debug

### Opening the Project

TODO

### Building the Project

#### Environment Variables

The project uses some sensitive environment variables:

- `WIUS_WIFI_SSID`: The WiFi SSID to connect to
- `WIUS_WIFI_PASS`: The WiFi password to connect to the SSID

These are not included in the base project. You need to set these up manually. There is two ways to do this:

##### `env.h` File

The compiler searches for the `env.h` file in the root directory. You can create this file and add the following lines:

```c
#ifndef ENV_H
#define ENV_H

#define WIUS_WIFI_SSID "<your_wifi_ssid>"
#define WIUS_WIFI_PASS "<your_wifi_password>"

#endif /* ENV_H */
```

Where `<your_wifi_ssid>` and `<your_wifi_password>` are the WiFi SSID and password you want to use.

##### `.env` File

You can also create a `.env` file in the root directory. Add the following lines:

```bash
WIUS_WIFI_SSID=<your_wifi_ssid>
WIUS_WIFI_PASS=<your_wifi_password>
```

Where `<your_wifi_ssid>` and `<your_wifi_password>` are the WiFi SSID and password you want to use.

This `.env` file is then compiled into above `env.h` file using the [`scripts/fetch_env.py`](scripts/fetch_env.py) script. You can use it using the following command:

```bash
python scripts/fetch_env.py .env env.h
```

Or via `make user/env.h`.

#### Building Setup

TODO

#### Subsequent Builds

TODO

### Flashing the Project

TODO

### Debugging the Project

TODO

## Code Structure

The code is structured to be modular and easy to understand. All of the code which is written by us is in the `user` directory. The code is divided into the following directories:
- `wius`: Low-level and Hardware-specific code for the WiUS PCB
  - Peripheral drivers
  - Networking drivers
  - etc.
- `tp`: TinyProbe-specific code built on top of the WiUS code
  - Power Management
  - AFE/TX drivers
  - Command handlers
  - etc.
- Other, common code that is used by both WiUS and TinyProbe
  - `user.h/user.c`: User entry point for the firmware
  - `log.h/log.c`: Logging code
  - `common.h/common.c`: Common code that is used by both WiUS and TinyProbe
  - `config.h`: Constants and configuration code

## Licensing

WiSeConnect 3 SDK is covered by one of several different licenses. The default license is the [Master Software License Agreement](https://www.silabs.com/about-us/legal/master-software-license-agreement) (MSLA), which applies unless otherwise noted. See [LICENSE.md](LICENSE.md) for full details.

This project in particular also uses code from the [FreeRTOS](https://github.com/FreeRTOS) project, which is licensed under the [MIT License](https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/LICENSE.md), as well as code from the [CMSIS library](https://github.com/ARM-software/CMSIS_6), which is licensed under the [Apache License 2.0](https://github.com/ARM-software/CMSIS_6/blob/main/LICENSE).


The code developed at [Integrated Systems Laboratory (IIS)](https://iis.ee.ethz.ch/) (ETH Zurich) is licensed under the Apache License 2.0.
