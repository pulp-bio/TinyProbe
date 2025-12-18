@defgroup tinyprobe TinyProbe Module
@brief Command processing, FPGA/AFE control, and probe orchestration

# TinyProbe Module

TinyProbe translates incoming control messages into hardware actions on the probe. It owns the command registry, FPGA/AFE access, and buffers that feed outbound data paths.

## Architecture
- Command dispatch: parsing and routing in [tp_command.h](tp_command.h)
- Command handlers: grouped under [TinyProbe Commands](commands/module.md) with one handler per opcode
- Hardware control: FPGA and AFE accessors in [tp_fpga.h](tp_fpga.h) and [tp_afe.h](tp_afe.h)
- Buffering: circular buffer helpers in [tp_buffer.h](tp_buffer.h)

## Data Flow (high level)
1. WiUS transport receives a message and forwards it to the TinyProbe command layer.
2. The dispatcher in `tp_command_execute()` selects the matching handler from [TinyProbe Commands](commands/module.md).
3. Handlers perform register writes/reads through FPGA/AFE helpers and may enqueue data into probe buffers.
4. Replies (if enabled) are returned via the WiUS transport.

## Extending TinyProbe
- Add a new command: create `tp_command_<name>.c/.h`, register the opcode in `tp_command_table`, and document it under [TinyProbe Commands](commands/module.md).
- Touch hardware safely: prefer helper APIs in `tp_fpga`/`tp_afe` rather than raw register writes to keep side effects contained.

@addtogroup tinyprobe
@{
@}