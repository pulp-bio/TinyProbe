

# Group common



[**Modules**](modules.md) **>** [**common**](group__common.md)



_Shared utilities, HAL glue, and logging used across TinyProbe and WiUS._ [More...](#detailed-description)








## Files

| Type | Name |
| ---: | :--- |
| file | [**common.c**](common_8c.md) <br>_Common source file._  |
| file | [**common.h**](common_8h.md) <br>_Common header file._  |
| file | [**config.h**](config_8h.md) <br>_Configuration header file._  |
| file | [**led.c**](led_8c.md) <br>_LED control implementation file._  |
| file | [**led.h**](led_8h.md) <br>_LED control header file._  |
| file | [**log.c**](log_8c.md) <br>_Logging implementation file._  |
| file | [**log.h**](log_8h.md) <br>_Logging header file._  |
| file | [**user.c**](user_8c.md) <br>_User main source file._  |
| file | [**user.h**](user_8h.md) <br>_User main header file._  |




## Modules

| Type | Name |
| ---: | :--- |
| module | [**Common firmware configurations**](group__config__common.md) <br> |






















































## Detailed Description


# Common Module




The common module provides shared glue that both [**TinyProbe**](group__tinyprobe.md) and [**WiUS**](group__wius.md) modules rely on. It contains lightweight utilities, logging, timing helpers, and macros that keep the platform code consistent across commands and transports.

## Purpose





* Provide common macros and helpers (see [**common.h**](common_8h.md))
* Offer a lightweight logging facade for all modules (see [**log.h**](log_8h.md))
* Centralize timing/delay helpers used by command handlers and drivers



## Key Pieces





* Logging: initialized via `log_init()` and consumed through `LOG_*` macros
* Time helpers: `delay_ms`, `delay_ns`, and `TICKS_PER_SEC` definitions
* Safety macros: `CHECK_STATUS`, `ASSERT`, and argument extraction helpers in commands



## Interactions





* Method handlers in [**TinyProbe Methods**](group__tinyprobe__methods.md) use the logging and argument macros from this module.
* WiUS transports depend on shared type and error definitions. 



    

------------------------------


