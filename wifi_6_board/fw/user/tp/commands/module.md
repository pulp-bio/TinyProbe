@defgroup tinyprobe_commands TinyProbe Commands
@ingroup tinyprobe
@brief Command handlers for TinyProbe control operations

# TinyProbe Commands

This group contains all command handlers used by TinyProbe to interact with hardware and system services. Each command implementation and its public interface lives in this subgroup to keep the command surface easy to navigate.

## Command Catalog
- Ping: @ref user/tp/commands/tp_command_ping.h "user/tp/commands/tp_command_ping.h" — reachability and identity check
- Trigger shot: @ref user/tp/commands/tp_command_triggershot.h "user/tp/commands/tp_command_triggershot.h" — trigger capture
- Delay ns/ms: @ref user/tp/commands/tp_command_delayns.h "user/tp/commands/tp_command_delayns.h" and @ref user/tp/commands/tp_command_sleepms.h "user/tp/commands/tp_command_sleepms.h" — timing control
- Power control/save: @ref user/tp/commands/tp_command_ctrlpwr.h "user/tp/commands/tp_command_ctrlpwr.h" and @ref user/tp/commands/tp_command_setpowersave.h "user/tp/commands/tp_command_setpowersave.h"
- SPI routing: @ref user/tp/commands/tp_command_swmux.h "user/tp/commands/tp_command_swmux.h" — select SPI MUX
- AFE/FPGA/SPI/TX writes: @ref user/tp/commands/tp_command_writeafe.h "user/tp/commands/tp_command_writeafe.h", @ref user/tp/commands/tp_command_writefpga.h "user/tp/commands/tp_command_writefpga.h", @ref user/tp/commands/tp_command_writespi.h "user/tp/commands/tp_command_writespi.h", @ref user/tp/commands/tp_command_writetx.h "user/tp/commands/tp_command_writetx.h"
- Enable replies: @ref user/tp/commands/tp_command_enreplies.h "user/tp/commands/tp_command_enreplies.h" — control response behavior

## How Commands Are Dispatched
1. Incoming packets are parsed in the TinyProbe dispatcher (see @ref user/tp/tp_command.c "user/tp/tp_command.c").
2. The dispatcher looks up the opcode in the command table and calls the corresponding handler from this group.
3. Handlers validate arguments, perform hardware actions through @ref common helpers and TinyProbe drivers, and optionally return data via WiUS.

## Adding a New Command
- Create `tp_command_<name>.c/.h` under `user/tp/commands/`.
- Register it in the command table alongside its opcode and expected argument length.
- Document it in this catalog and keep the description concise (what it does, inputs, side effects).

@addtogroup tinyprobe_commands
@{
Keep the catalog above current when adding or removing commands so downstream consumers know what is available.
@}