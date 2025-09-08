# TinyProbe Python API

High‑level Python tooling to set up, connect to, and stream data from TinyProbe.

## Requirements

The development of the Python API was done with [uv](https://astral.sh/uv/) as the Python package and project manager.

Please download and [install](https://docs.astral.sh/uv/#installation) uv first.

To then set up the environment, run
```bash
uv sync
```
In this directory (where `uv.lock` and `pyproject.toml` are located). This will create a virtual environment (default: `.venv`) and install the needed Python version and dependencies.

## Notebook

The API is best used in a Jupyter notebook. To start one, run
```bash
uv run jupyter notebook
```
in this directory and open the notebook `main.ipynb`.