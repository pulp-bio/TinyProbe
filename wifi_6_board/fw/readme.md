# WiUS (Wireless Ultrasound) Firmware - TinyProbe WiFi v2

- [WiUS (Wireless Ultrasound) Firmware - TinyProbe WiFi v2](#wius-wireless-ultrasound-firmware---tinyprobe-wifi-v2)
  - [Requisites](#requisites)
  - [Build, Flash and Debug](#build-flash-and-debug)
      - [Opening the Project](#opening-the-project)
    - [Building the Project](#building-the-project)
      - [Environment Variables](#environment-variables)
        - [`env.h` File](#envh-file)
        - [`.env` File](#env-file)
      - [Building in Simplicity Studio](#building-in-simplicity-studio)
      - [Building with CMake (Optional)](#building-with-cmake-optional)
    - [Flashing the Project](#flashing-the-project)
    - [Debugging the Project](#debugging-the-project)
  - [Code Structure](#code-structure)
  - [Licensing](#licensing)


## Requisites

In order to use this firmware, you need to install Simplicity Studio. You can download it from the [Silicon Labs website](https://www.silabs.com/developers/simplicity-studio).

To get an introduction to Simplicity Studio, check the [Developing with WiSeConnect™ SDK v3.x with SiWx91x™ Boards](https://docs.silabs.com/wiseconnect/latest/wiseconnect-developers-guide-developing-for-silabs-hosts/) guide.

## Build, Flash and Debug

#### Opening the Project

To open this project in Simplicity Studio, you need to:

1. In Simplicity Studio, click on `Import projects...` in the Project Explorer view
2. Select `Existing Projects into Workspace` and click `Next`
3. Under `Select root directory`, click `Browse...` and select the root directory of this repository
4. The `wius_fw` project should be listed. Make sure it is checked.
5. All the options below should be unchecked.
6. Click `Finish`

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

Or via `make env.h`.

#### Building in Simplicity Studio

To build the project in Simplicity Studio, you need to do the following:

1. Import the project into Simplicity Studio as described above
2. Define the environment variables as described above
3. In the Project Explorer view, find the `wius_fw.slcp` file and open it
4. In the middle "Project Details" column, click on the three dots and on `Force Generation`
5. Wait until the generation is finished (you can see the progress on the bottom right corner)
6. Make sure the project is selected in the Project Explorer view
7. Click on the `Build` button in the toolbar (or press `Ctrl+B`)
8. Wait for the build to finish (you can see the progress in the Console view)
9. If the build is successful, you will see `DONE` in the Console

#### Building with CMake (Optional)

If you want to build the project using CMake, you need to do the following:

1. Generate the build files using Simplicity Studio
   1. Open the project in Simplicity Studio
   2. Open the project file [`wius_fw.slcp`](wius_fw.slcp)
   3. In the middle "Project Details" column, click on the three dots and on `Force Generation`
2. Open [`wius_fw_cmake/CMakeLists.txt`](wius_fw_cmake/CMakeLists.txt)
   1. To add the [`user`](user) directory
   2. To include the `common` library

    Change
    ```cmake
    # Link with the content defined in the SLC project
    target_link_libraries(wius_fw PRIVATE
        slc_wius_fw
    )
    ```
    to
    ```cmake
    add_subdirectory(../user ${CMAKE_BINARY_DIR}/user)

    # Link with the content defined in the SLC project
    target_link_libraries(wius_fw PRIVATE
        slc_wius_fw
        common
    )
    ```

3. Build the project using make in the root directory
    ```bash
    make
    ```

### Flashing the Project

1. Make sure WiUS is attached to the computer via the Simplicity Mini connector of the dev board.
2. Right click on the project and click `Run As > 1 Silicon Labs ARM Program`
3. You should see a success message in the Console view

### Debugging the Project

1. Make sure WiUS is attached to the computer via the Simplicity Mini connector of the dev board.
2. Right click on the project and click `Debug As > 1 Silicon Labs ARM Debug Session`
3. You should see the Debug perspective open with the project loaded

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
