@defgroup tinyprobe TinyProbe Module
@brief Method processing, FPGA/AFE control, and probe orchestration

# TinyProbe Module

TinyProbe translates incoming control messages into hardware actions on the probe. It owns the method registry, FPGA/AFE access, and buffers that feed outbound data paths.

## Architecture

- Method dispatch: protobuf request decoding and routing in @ref tp_methods.h
- Method handlers: grouped under @ref tinyprobe_methods "TinyProbe Methods" with one handler per generated method
- Hardware control: FPGA, AFE, TX, mux, and power accessors in @ref tp_fpga.h, @ref tp_afe.h, @ref tp_tx.h, @ref tp_mux.h, and @ref tp_power.h
- Buffering: circular buffer helpers in @ref tp_buffer.h

## Data Flow (high level)

1. WiUS transport receives a message and forwards it to the TinyProbe method layer.
2. `tp_methods_handle()` decodes the nanopb request and selects the matching handler from @ref tinyprobe_methods "TinyProbe Methods".
3. Handlers perform register writes/reads through TinyProbe helpers and may enqueue data into probe buffers.
4. Status replies are encoded as protobuf responses and returned via the WiUS transport.

## Extending TinyProbe

- Add a new method: update the generated method definition, create `tp_method_<name>.c/.h`, add it to `TP_METHODS`, and document it under @ref tinyprobe_methods "TinyProbe Methods".
- Touch hardware safely: prefer helper APIs in `tp_fpga`, `tp_afe`, `tp_tx`, `tp_mux`, and `tp_power` rather than open-coded register writes to keep side effects contained.

@addtogroup tinyprobe
@{
@}
