# FPGA tests

Use Git Bash, Just, Questa, Python 3.11 and cocotb 2.0.1 on `PATH`.

```bash
just fpga test
just fpga test waveform_gen pulse_mode
```

For vendor-FIFO tests, generate the Hog project first:

```bash
export LIBERO_ROOT=/path/to/Libero_SoC
just fpga test fifo_accumulator accumulation_pipeline --fifo libero
```
