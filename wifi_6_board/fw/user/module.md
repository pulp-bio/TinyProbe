@defgroup common Common Module
@brief Shared utilities, HAL glue, and logging used across TinyProbe and WiUS

# Common Module

The common module provides shared glue that both [TinyProbe](tp/module.md) and [WiUS](wius/module.md) rely on. It contains lightweight utilities, logging, timing helpers, and macros that keep the platform code consistent across commands and transports.

## Purpose
- Provide common macros and helpers (see [common.h](common.h))
- Offer a lightweight logging facade for all modules (see [log.h](log.h))
- Centralize timing/delay helpers used by command handlers and drivers

## Key Pieces
- Logging: initialized via `log_init()` and consumed through `LOG_*` macros
- Time helpers: `delay_ms`, `delay_ns`, and `TICKS_PER_SEC` definitions
- Safety macros: `CHECK_STATUS`, `ASSERT`, and argument extraction helpers in commands

## Interactions
- Command handlers in [TinyProbe Commands](tp/commands/module.md) use the logging and argument macros from this module.
- WiUS transports depend on shared type and error definitions.

@addtogroup common
@{
@}