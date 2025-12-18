@defgroup tinyprobe TinyProbe Module
@brief Command processing, FPGA/AFE control, and probe orchestration

# TinyProbe Overview
TinyProbe translates incoming control messages into hardware actions on the probe. It owns the command registry, FPGA/AFE access, and buffers that feed outbound data paths.

## Architecture
- Command dispatch: parsing and routing in @ref user/tp/tp_command.h "user/tp/tp_command.h" and @ref user/tp/tp_command.c "user/tp/tp_command.c"
- Command handlers: grouped under @ref tinyprobe_commands with one handler per opcode
- Hardware control: FPGA and AFE accessors in @ref user/tp/tp_fpga.h "user/tp/tp_fpga.h" and @ref user/tp/tp_afe.h "user/tp/tp_afe.h"
- Buffering: circular buffer helpers in @ref user/tp/tp_buffer.h "user/tp/tp_buffer.h"

## Data Flow (high level)
1. WiUS transport receives a message and forwards it to the TinyProbe command layer.
2. The dispatcher in `tp_command_execute()` selects the matching handler from @ref tinyprobe_commands.
3. Handlers perform register writes/reads through FPGA/AFE helpers and may enqueue data into probe buffers.
4. Replies (if enabled) are returned via the WiUS transport.

## Extending TinyProbe
- Add a new command: create `tp_command_<name>.c/.h`, register the opcode in `tp_command_table`, and document it under @ref tinyprobe_commands.
- Touch hardware safely: prefer helper APIs in `tp_fpga`/`tp_afe` rather than raw register writes to keep side effects contained.

@addtogroup tinyprobe
@{
Use this group for core TinyProbe orchestration topics: new command plumbing, buffer lifetime rules, and coordination with WiUS transports.
@}