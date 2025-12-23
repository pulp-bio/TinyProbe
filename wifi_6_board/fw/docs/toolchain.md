# Getting started with the Silicon Labs Toolchain

## Installation

> Official Instructions can be found [here](https://docs.silabs.com/ssv6ug/latest/install-ssv6/install-simplicity-studio)

### Simplicity Studio v6

1. Download and install Simplicity Studio v6 from [here](https://www.silabs.com/software-and-tools/simplicity-studio?tab=getting-started)
2. Launch `Simplicity Installer`
3. Select `Technology Install`
4. Make sure `Wi-Fi` is selected under `Optional Packages`
5. Click `Next`
6. Agree to the license terms and click `Install`. This may take a while.
7. Click `Launch Studio`

### Visual Studio Code

1. Download and install Visual Studio Code from [here](https://code.visualstudio.com/download)
2. Launch Visual Studio Code

### Visual Studio Code Extension

1. (Optional, highly recommended): Set up a new, dedicated profile for Silicon Labs development (see [here](https://code.visualstudio.com/docs/configure/profiles))
2. Install the `Simplicity Studio for VS Code` extension by `Silicon Labs`

### Linux: udev rules

**Note:** No similar step like this is required on Windows

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

1. In the `Home` tab of Simplicity Studio, click `(all projects & demos)`
2. Make sure `Simplicity SDK Suite v2025.x.y` (tested: `v2025.6.2`) is selected in the top right corner
3. Click `Select Device` in the top right
4. Enter and select your dev board (tested: `SiWx917-DK2605A`, in list as `BRD2605A`)
5. Search for the `Wi-Fi - SNTP Client (SoC)` project
6. Click `Create`
7. Make sure under `Target IDE`, `VS Code (GCC)` is chosen
8. If desired, change the `Project Name` and `Location`
9. Click `Finish`

## Building and flashing the example project

### Opening the project

1. In the resulting project window, click `Open in VS Code` in the top right corner
2. Simplicity Studio may complain about the Extension not being installed, but the project should open fine in VS Code. Just make sure the correct profile is selected, if you created one
3. In the Simplicity Studio for VS Code extension tab, the example project should be listed under `Untitled (Workspace)`

### Adjusting the project configuration

1. Extend the project list item by clicking the small arrow to the left of the project name
2. Expand the `config` folder
3. Open *sl_net_default_values.h*
4. Adjust the following macros as needed:
   ```c
   #define DEFAULT_WIFI_CLIENT_PROFILE_SSID "<Your SSID>"
   #define DEFAULT_WIFI_CLIENT_PROFILE_PASSWORD "<Your Password>"
   ```
5. Save the file (`Ctrl+S`)

### Building the project

1. Click the `Build` button (hammer icon) in the project list item
2. The following should appear in the `Output` tab at the bottom:
   ```
   Build of Project <Project Name> with configuration default_config was successfully finished.
   ```

### Flashing the project

1. Connect your dev board to your PC via USB
2. Click the `Flash` button (chip icon) in the project list item
3. Select the `.hex` file in the dialog
4. The following should appear in the `Output` tab at the bottom:
   ```
   Flash of '<Board Name>' with binary '<Binary File>' was successfully finished.
   ```

## Running the example project

1. Open a serial terminal (I suggest using the `Serial Monitor` extension by `Microsoft` for VS Code)
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

1. In Simplicity Studio, select the project in the `Projects` view
2. Click on the file ending with `.slcp`
3. The project overview should open
4. Click on the `Software Components` tab

First, we need to remove the existing `System Calls` component, as it conflicts with the RTT component we want to add.

5. Search and uninstall `System Calls`

Then, we can add the required components for RTT support in STDIO.

6. Search and install `IO Stream:SI91X RTT`
7. Search and install `IO Stream: Retarget STDIO`

### Generating the updated project

Generally, the project configurator should automatically generate the updated project after making changes. If it does not (subsequent builds do not work), you can manually trigger it:

1. Go to the project overview (file ending with `.slcp`)
2. In the `Project Details` column in the middle, click on the three dots on top and select `Force Generation`

**Note:** Sometimes, certain auto-generated files in `autogen` or `config` get corrupted after adding/removing packages. These corrupted files will then cause errors in new builds. I needed to manually delete these files (for example `config/pin_config.h`) and force regeneration again.

### Using RTT in your code

1. Since RTT also listens to the standard output, we do not need to change anything in the code
2. Build and flash the updated project as described above
3. Open a RTT viewer. Simplicity Studio has a built-in one:
   1. `Tools` -> `Commander` -> `Open Tool`
   2. In the top left, select your connected board
   3. In the left sidebar, select `RTT`
   4. Click `Connect`
   5. Now, you should see the same output as before, but in the RTT viewer instead of a serial terminal

## Simplicity Commander

Sometimes, development using CLI tools is desired rather than a GUI-centric approach. Silicon Labs provides the `Simplicity Commander` tool for this purpose.

It can be found in the Simplicity Studio installation directory, for example:

```bash
~/.silabs/slt/installs/archive/Simplicity Commander/commander.exe # Windows
~/.silabs/slt/installs/archive/commander/commander     # Linux/macOS
```

With this tool, we can

- Flash binaries to connected devices
- Open communication channels (UART, RTT, ...)

Please take a look at the Makefile in the root of this firmware directory for usage examples.
