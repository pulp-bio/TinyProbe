# Getting started with the Silicon Labs Toolchain

- [Getting started with the Silicon Labs Toolchain](#getting-started-with-the-silicon-labs-toolchain)
  - [Installation](#installation)
    - [Simplicity Studio v6](#simplicity-studio-v6)
    - [Visual Studio Code](#visual-studio-code)
    - [Visual Studio Code Extension](#visual-studio-code-extension)
    - [Linux: udev rules](#linux-udev-rules)
  - [Setting up an example project](#setting-up-an-example-project)
  - [Building and flashing the example project](#building-and-flashing-the-example-project)
    - [Opening the project](#opening-the-project)
    - [Adjusting the project configuration](#adjusting-the-project-configuration)
    - [Building the project](#building-the-project)
    - [Flashing the project](#flashing-the-project)
  - [Running the example project](#running-the-example-project)
  - [Adding a component (Using RTT)](#adding-a-component-using-rtt)
    - [Generating the updated project](#generating-the-updated-project)
    - [Using RTT in your code](#using-rtt-in-your-code)
  - [Simplicity Commander](#simplicity-commander)

## Installation

> Official Instructions can be found [here](https://docs.silabs.com/ssv6ug/latest/install-ssv6/install-simplicity-studio)

### Simplicity Studio v6

1. Download and install Simplicity Studio v6 from [here](https://www.silabs.com/software-and-tools/simplicity-studio?tab=getting-started)
2. Launch _Simplicity Installer_
3. Select _Technology Install_
4. Make sure _Wi-Fi_ is selected under _Optional Packages_
5. Click _Next_
6. Agree to the license terms and click _Install_. This may take a while.
7. Click _Launch Studio_

### Visual Studio Code

1. Download and install Visual Studio Code from [here](https://code.visualstudio.com/download)
2. Launch Visual Studio Code

### Visual Studio Code Extension

1. (Optional, highly recommended): Set up a new, dedicated profile for Silicon Labs development (see [here](https://code.visualstudio.com/docs/configure/profiles))
2. Install the _Simplicity Studio for VS Code_ extension by _Silicon Labs_

### Linux: udev rules

1. Download this udev rules file: [69-probe-rs.rules](https://probe.rs/files/69-probe-rs.rules)
2. Place it in `/etc/udev/rules.d/` via
   ```bash
   sudo cp 69-probe-rs.rules /etc/udev/rules.d/
   ```
3. Reload udev rules via
   ```bash
   sudo udevadm control --reload
   sudo udevadm trigger
   ```

## Setting up an example project

> Official Instructions can be found [here](https://docs.silabs.com/ssv6ug/latest/ssv6-create-project/)

1. In the _Home_ tab of Simplicity Studio, click _(all projects & demos)_
2. Make sure _Simplicity SDK Suite v2025.x.y_ (tested: _v2025.6.2_) is selected in the top right corner
3. Click _Select Device_ in the top right
4. Enter and select your dev board (tested: _SiWx917-DK2605A_, in list as _BRD2605A_)
5. Search for the _Wi-Fi - SNTP Client (SoC)_ project
6. Click _Create_
7. Make sure under _Target IDE_, _VS Code (GCC)_ is chosen
8. If desired, change the _Project Name_ and _Location_
9. Click _Finish_

## Building and flashing the example project

### Opening the project

1. In the resulting project window, click _Open in VS Code_ in the top right corner
2. Simplicity Studio may complain about the Extension not being installed, but the project should open fine in VS Code. Just make sure the correct profile is selected, if you created one
3. In the Simplicity Studio for VS Code extension tab, the example project should be listed under _Untitled (Workspace)_

### Adjusting the project configuration

1. Extend the project list item by clicking the small arrow to the left of the project name
2. Expand the _config_ folder
3. Open *sl_net_default_values.h*
4. Adjust the following macros as needed:
   ```c
   #define DEFAULT_WIFI_CLIENT_PROFILE_SSID "<Your SSID>"
   #define DEFAULT_WIFI_CLIENT_PROFILE_PASSWORD "<Your Password>"
   ```
5. Save the file (`Ctrl+S`)

### Building the project

1. Click the _Build_ button (hammer icon) in the project list item
2. The following should appear in the _Output_ tab at the bottom:
   ```
   Build of Project <Project Name> with configuration default_config was successfully finished.
   ```

### Flashing the project

1. Connect your dev board to your PC via USB
2. Click the _Flash_ button (chip icon) in the project list item
3. Select the _.hex_ file in the dialog
4. The following should appear in the _Output_ tab at the bottom:
   ```
   Flash of '<Board Name>' with binary '<Binary File>' was successfully finished.
   ```

## Running the example project

1. Open a serial terminal (I suggest using the _Serial Monitor_ extension by _Microsoft_ for VS Code)
2. You should see the following output:
   ```
   SNTP client execution Started 
   Wi-Fi client connected
   Ip Address : 185.125.24.59
    
   Received SNTP Client Start SNTP event with status Success
    
   Received SNTP Client Get Time SNTP event with status Success
   Time: 3973759073. sec.
    
   Received SNTP Client Get Time and Date SNTP event with status Success
   Dec 3, 2025 13:57:53.422 UTC 
    
   Received SNTP Client Get Server Info SNTP event with status Success
   Got Server IP version as : 4
   IPv4 Address is : 185.125.24.59
   SNTP Server Method : 2
    
   Received SNTP Client Stop SNTP event with status Success
   Done
   SNTP client execution completed 
   ```
3. If you see this output, congratulations! You have successfully built, flashed, and run your first Silicon Labs Wi-Fi example project!

## Adding a component (Using RTT)

> Official Instructions can be found [here](https://docs.silabs.com/ssv6ug/latest/ssv6-configure-project/project-configurator)

1. In Simplicity Studio, select the project in the _Projects_ view
2. Click on the file ending with _.slcp_
3. The project overview should open
4. Click on the _Software Components_ tab

First, we need to remove the existing _System Calls_ component, as it conflicts with the RTT component we want to add.

5. Search and uninstall _System Calls_

Then, we can add the required components for RTT support in STDIO.

6. Search and install _IO Stream:SI91X RTT_
7. Search and install _IO Stream: Retarget STDIO_

### Generating the updated project

Generally, the project configurator should automatically prompt you to generate the updated project after making changes. If it does not (subsequent builds do not work), you can manually trigger it:

1. Go to the project overview (file ending with _.slcp_)
2. In the _Project Details_ column in the middle, click on the three dots on top and select _Force Generation_

Sometimes, I needed to manually delete certain files which get corrupted (for example `config/pin_config.h`) and force regeneration again.

### Using RTT in your code

1. Since RTT also listens to the standard output, we do not need to change anything in the code
2. Build and flash the updated project as described above
3. Open a RTT viewer. Simplicity Studio has a built-in one:
   1. _Tools_ -> _Commander_ -> _Open Tool_
   2. In the top left, select your connected board
   3. In the left sidebar, select _RTT_
   4. Click _Connect_
   5. Now, you should see the same output as before, but in the RTT viewer instead of a serial terminal

## Simplicity Commander

Sometimes, development using CLI tools is desired rather than a GUI-centric approach. Silicon Labs provides the _Simplicity Commander_ tool for this purpose.

It can be found in the Simplicity Studio installation directory, for example:

```bash
~/.silabs/slt/installs/archive/Simplicity Commander/commander.exe # Windows
~/.silabs/slt/installs/archive/commander /commander     # Linux/macOS
```

With this tool, we can

- Flash binaries to connected devices
- Open communication channels (UART, RTT, ...)

I personally use this Makefile:

```make
PROJECT_NAME := fw_v6
CMAKE_DIR := cmake_gcc

PYTHON ?= python
COMMANDER ?= "~/.silabs/slt/installs/archive/Simplicity Commander/commander.exe"

build:
	cmake --build cmake_gcc/build

flash: build
	$(COMMANDER) flash cmake_gcc/build/base/$(PROJECT_NAME).hex --device SIWG917

attach:
	sleep 1.5
	$(COMMANDER) rtt connect --device SIWG917 --speed 2500 --noreset

attach_reset:
	$(COMMANDER) rtt connect --device SIWG917 --speed 2500

clean:
	rm -rf $(CMAKE_DIR)/build

.PHONY: build flash attach attach_reset clean
```