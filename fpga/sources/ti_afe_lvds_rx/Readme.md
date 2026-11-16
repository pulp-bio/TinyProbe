# LVDS receiver RTL for TI AFEs

The `src/` modules receive serialized AFE IC LVDS data using DCLK and
align the parallel output to FCLK. The board wrapper is `common/afe_rx.sv`.

See [FPGA tests](../../tests/README.md) for the current test commands.
