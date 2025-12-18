@defgroup common Common Module
@brief Shared utilities, HAL glue, and logging used across TinyProbe and WiUS

# Common Overview
The common module provides shared glue that both @ref tinyprobe and @ref wius rely on. It contains lightweight utilities, logging, timing helpers, and macros that keep the platform code consistent across commands and transports.

## Purpose
- Provide common macros and helpers
- Offer a lightweight logging facade for all modules
- Centralize timing/delay helpers used by command handlers and drivers

## Key Pieces
- Logging: initialized via `log_init()` and consumed through `LOG_*` macros
- Time helpers: `delay_ms`, `delay_ns`, and `TICKS_PER_SEC` definitions
- Safety macros: `CHECK_STATUS`, `ASSERT`, and argument extraction helpers in commands

## Interactions
- Command handlers in @ref tinyprobe_commands use the logging and argument macros from this module.
- WiUS transports depend on shared type and error definitions.

@addtogroup common
@{
Use this group to document any shared utilities you add. Keep new helpers minimal and well-tested since they are used everywhere.
@}