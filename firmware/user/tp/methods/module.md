@defgroup tinyprobe_methods TinyProbe Methods
@ingroup tinyprobe
@brief Method handlers for TinyProbe control operations

# TinyProbe Methods

This group contains all method handlers used by TinyProbe to interact with hardware and system services. Each method implementation and its public interface lives in this subgroup to keep the method surface easy to navigate.

## Method Catalog

| Method | Header | Description |
|---------|--------|-------------|
| Ping | @ref tp_method_ping.h | Reachability and identity check |
| Trigger shot | @ref tp_method_triggershot.h | Trigger capture |
| Delay ns | @ref tp_method_delayns.h | Nanosecond timing control |
| Delay ms | @ref tp_method_delayms.h | Millisecond timing control |
| Power control | @ref tp_method_controlpower.h | Toggle power rails |
| Set log level | @ref tp_method_setloglevel.h | Configure firmware log verbosity |
| SPI MUX | @ref tp_method_controlspi.h | Select SPI MUX target |
| Write AFE | @ref tp_method_writeafe.h | AFE register write |
| Write FPGA | @ref tp_method_writefpga.h | FPGA register write |
| Write TX | @ref tp_method_writetx.h | TX buffer write |

## How Methods Are Dispatched

1. Incoming framed protobuf packets are decoded by `tp_methods_handle()` in @ref tp_methods.h.
2. The dispatcher switches on the generated nanopb oneof tag and calls the corresponding handler from this group.
3. Handlers validate arguments, perform hardware actions through @ref common "common" helpers and TinyProbe drivers, and return a generated status code.

## Adding a New Method

- Create `tp_method_<name>.c/.h` under `user/tp/methods/`.
- Add it to the generated method definition and include it in the `TP_METHODS` macro.
- Document it in this catalog and keep the description concise (what it does, inputs, side effects).

@addtogroup tinyprobe_methods
@{
@}
