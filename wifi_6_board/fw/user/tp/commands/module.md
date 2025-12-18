@defgroup tinyprobe_commands TinyProbe Commands
@ingroup tinyprobe
@brief Command handlers for TinyProbe control operations

# TinyProbe Commands

This group contains all command handlers used by TinyProbe to interact with hardware and system services. Each command implementation and its public interface lives in this subgroup to keep the command surface easy to navigate.

## Command Catalog
| Command | Header | Description |
|---------|--------|-------------|
| Ping | [tp_command_ping.h](tp_command_ping.h) | Reachability and identity check |
| Trigger shot | [tp_command_triggershot.h](tp_command_triggershot.h) | Trigger capture |
| Delay ns | [tp_command_delayns.h](tp_command_delayns.h) | Nanosecond timing control |
| Sleep ms | [tp_command_sleepms.h](tp_command_sleepms.h) | Millisecond timing control |
| Power control | [tp_command_ctrlpwr.h](tp_command_ctrlpwr.h) | Toggle power rails |
| Set powersave | [tp_command_setpowersave.h](tp_command_setpowersave.h) | Configure power mode |
| SPI MUX | [tp_command_swmux.h](tp_command_swmux.h) | Select SPI MUX target |
| Write AFE | [tp_command_writeafe.h](tp_command_writeafe.h) | AFE register write |
| Write FPGA | [tp_command_writefpga.h](tp_command_writefpga.h) | FPGA register write |
| Write SPI | [tp_command_writespi.h](tp_command_writespi.h) | Raw SPI transfer |
| Write TX | [tp_command_writetx.h](tp_command_writetx.h) | TX buffer write |
| Enable replies | [tp_command_enreplies.h](tp_command_enreplies.h) | Control response behavior |

## How Commands Are Dispatched
1. Incoming packets are parsed in the TinyProbe dispatcher (see [tp_command.h](../tp_command.h)).
2. The dispatcher looks up the opcode in the command table and calls the corresponding handler from this group.
3. Handlers validate arguments, perform hardware actions through [common](../../module.md) helpers and TinyProbe drivers, and optionally return data via WiUS.

## Adding a New Command
- Create `tp_command_<name>.c/.h` under `user/tp/commands/`.
- Register it in the command table alongside its opcode and expected argument length.
- Document it in this catalog and keep the description concise (what it does, inputs, side effects).

@addtogroup tinyprobe_commands
@{
@}