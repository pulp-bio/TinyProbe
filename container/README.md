# TinyProbe Development Containers

The containers provide a fully self-contained firmware build environment for the SiWG917 target.
They bundle the Silicon Labs toolchain: `slt`, `slc`, `cmake`, `ninja`, ARM GCC 12.2, `commander`, `sdm`, Simplicity SDK 2025.6.2, and WiseConnect 3.5.2, so no host-side Silicon Labs installation is required.

Two container formats are provided:

| Format | File | Use case |
|--------|------|----------|
| Docker | `Dockerfile` | Local development, CI/CD |
| Apptainer (Singularity) | `container.def` | HPC clusters, rootless environments |

All recipes are managed with `just`. Run `just` from this directory to list them.

## Prerequisites

### SLT installer zip (both formats)

The Silicon Labs `slt-cli` installer is not redistributed in this repository.
Download `slt-cli-1.0.1-linux-x64.zip` from [Silicon Labs](https://www.silabs.com/documents/public/software/slt-cli-1.0.1-linux-x64.zip) directly
and place it next to the `Dockerfile` / `container.def` before building:

```
container/
├── slt-cli-1.0.1-linux-x64.zip  # place here
├── Dockerfile
├── container.def
└── ...
```

## Quick start

### Docker

```bash
# Build the image (once)
just build

# Run a shell with the firmware directory mounted
just run

# Run with a custom directory
just run /path/to/your/dir
```

### Apptainer

```bash
# Build the SIF image (once, needs the zip next to container.def)
just build_appt

# Open a shell with the repo root bound into the container
just run_appt

# Run with a custom directory
just run_appt /path/to/your/dir
```

## Available recipes

```
build        Build the Docker image
build_appt   Build the Apptainer SIF image
pack         Export the Docker image to a gzipped tarball
load         Import a previously packed Docker image tarball
run          Run a Docker shell with the firmware directory mounted
run_appt     Open an Apptainer shell with the repo root bound
publish      Tag and push the Docker image to Docker Hub
```

## Installed toolchain

The build environment installs the following via `slt` (`cli_tools.toml`):

| Tool | Version |
|------|---------|
| cmake | latest |
| commander | latest |
| gcc-arm-none-eabi | 12.2.rel1 |
| ninja | latest |
| sdm | latest |
| simplicity-sdk | 2025.6.2 |
| slc\_cli | latest |
| wiseconnect | 3.5.2 |

After installation `PATH`, `ARM_GCC_DIR`, `SLC_SDK`, and `POST_BUILD_EXE` are set automatically
so that `slc`, `cmake`, `ninja`, and `commander` are available in every shell session.

## Docker Hub

To publish the Docker image to Docker Hub:

```bash
just publish <your-dockerhub-username>
# or with a custom image name
just publish <your-dockerhub-username> my-image-name
```

## Dev Containers (VS Code / Cursor)

Both container flavours can be used as a Dev Container.

### Docker

Add a `.devcontainer/devcontainer.json` in the repository root that points to this `Dockerfile`:

```json
{
  "name": "TinyProbe firmware",
  "build": { "context": "container", "dockerfile": "container/Dockerfile" },
  "workspaceMount": "source=${localWorkspaceFolder}/firmware,target=/work,type=bind",
  "workspaceFolder": "/work"
}
```

### Apptainer

Add the following to `~/.ssh/config` to add an SSH configuration for the Apptainer container:

```
Host tinyprobe-apptainer
  HostName <your hostname>
  User <your username>
  RemoteCommand cd /path/to/this/repo && just container run_appt
  RequestTTY yes
```

Check if the configuration is working by trying to SSH into the container:

```bash
ssh tinyprobe-apptainer
```

If you see a `Apptainer>` prompt, the configuration is working.

Now, we need to set a global setting in VS Code to allow the container to install the VS Code server. Open the Command Palette (Ctrl+Shift+P) and search for "Preferences: Open User Settings (JSON)". Add the following settings:

```json
"remote.SSH.enableRemoteCommand": true,
"remote.SSH.serverInstallPath": {
    "apptainer": "/path/to/this/repo/.vscode_server"
}
```

You can now use the container as a Dev Container in VS Code by connecting to `tinyprobe-apptainer` via SSH. See [VS Code Remote - SSH](https://code.visualstudio.com/docs/remote/ssh#_connect-to-a-remote-host) for details. In short: Open command palette, search for "Remote-SSH: Connect to Host...", and select `tinyprobe-apptainer`. The container will be started and the VS Code server will be installed automatically.
