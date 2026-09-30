

# File module.md

[**File List**](files.md) **>** [**module.md**](module_8md.md)

[Go to the documentation of this file](module_8md.md)


```Markdown
@defgroup common Common Module
@brief Shared utilities, HAL glue, and logging used across TinyProbe and WiUS

# Common Module

The common module provides shared glue that both @ref tinyprobe "TinyProbe" and @ref wius "WiUS" modules rely on. It contains lightweight utilities, logging, timing helpers, and macros that keep the platform code consistent across commands and transports.

## Purpose
- Provide common macros and helpers (see @ref common.h)
- Offer a lightweight logging facade for all modules (see @ref log.h)
- Centralize timing/delay helpers used by command handlers and drivers

## Key Pieces
- Logging: initialized via `log_init()` and consumed through `LOG_*` macros
- Time helpers: `delay_ms`, `delay_ns`, and `TICKS_PER_SEC` definitions
- Safety macros: `CHECK_STATUS`, `ASSERT`, and argument extraction helpers in commands

## Interactions
- Method handlers in @ref tinyprobe_methods "TinyProbe Methods" use the logging and argument macros from this module.
- WiUS transports depend on shared type and error definitions.

@addtogroup common
@{
@}
```


