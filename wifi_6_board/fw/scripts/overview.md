# WiUS v6 firmware scripts

This repository contains scripts for interacting with the WiUS v6 firmware on Tinyprobe WiFi 6 boards. It includes tools for configuring the device, acquiring data, and processing responses.

## Prerequisites

These scripts were developed using the [uv](astral.sh/uv) environment manager. To set up the environment, run:

```bash
uv sync
```

Now, you can either activate the environment:

```bash
.venv\Scripts\activate.ps1 # On Windows
source .venv/bin/activate # On Unix or MacOS
```

Or just run the scripts using `uv run`:

```bash
uv run main.py
```

I suggest the latter, as it avoids potential issues with environment activation.

## Usage

### C header generation: [`to_header.py`](to_header.py)

This script generates a C header file from a configuration file, generally used for embedding environment variables like WiFi credentials into firmware code. Used in the main firmware build process.

The configuration file is a simple text file with `KEY=VALUE` pairs, one per line. Lines starting with `#` are treated as comments and ignored.

```bash
python to_header.py [-h] conf_file header_file
```

Positional arguments:

- **conf_file**:   Path to the configuration file
- **header_file**: Path to the output C header file

Options:

- **-h, --help**: show help message

### Keysight dlog parser: [`dlog.py`](dlog.py)

This script parses Keysight .dlog files and extracts/plots data for analysis. Taken directly from [derf/dlog-viewer](https://github.com/derf/dlog-viewer).

```bash
dlog.py [-h] [--csv-export FILENAME] [--json-export FILENAME] [--skip N] [--limit N] [--pelt NUM] [--plot-x {T,U,I,P}] [--plot-y {U,I,P,eta,all}] [--stat] dlog_file
```

Positional arguments:

- **dlog_file**: Input filename in Keysight dlog format

Options:

- **-h, --help**:             show help message
- **--csv-export FILENAME**:  Export measurements to CSV file
- **--json-export FILENAME**: Export analysis results (e.g. changepoints) to JSON file
- **--skip N**:               Skip the first N seconds of data. This is useful to avoid startup code influencing the results of a long-running measurement
- **--limit N**:              Limit analysis to the first N seconds of data
- **--pelt NUM**:             Perform changepoint detection on NUM samples
- **--plot-x {T,U,I,P}**:     Plot time/voltage/current/power at X axis
- **--plot-y, --plot {U,I,P,eta,all}**: Plot voltage/current/power/efficiency at Y axis
- **--stat**:                Print mean voltage, current, and power

### Main control script: [`main.py`](main.py)

TODO

## Licensing

The code developed at [Integrated Systems Laboratory (IIS)](https://iis.ee.ethz.ch/) (ETH Zurich) is licensed under the Apache License 2.0.
