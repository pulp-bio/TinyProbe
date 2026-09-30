

# File common.h

[**File List**](files.md) **>** [**common**](dir_85edcc1f099af2a701a791767791d401.md) **>** [**common.h**](common_8h.md)

[Go to the documentation of this file](common_8h.md)


```C++

#pragma once

// === Common Header Files ===
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "sl_status.h"
#include "cmsis_os2.h"

#include "config.h"
#include "log.h"
#include "led.h"

#define CONCAT_2(a, b) a##b
#define CONCAT_3(a, b, c) a##b##c

#define TICKS_PER_SEC (OS_Tick_GetClock() / OS_Tick_GetInterval())

#define LOG_STATUS(status) log_status(__FILE__, __LINE__, (status))

#define LOG_RET_STATUS(x)                        \
    do                                           \
    {                                            \
        sl_status_t _tmp_status = (x);           \
        LOG_STATUS(_tmp_status);                 \
        if (SL_STATUS_OK != _tmp_status)         \
        {                                        \
            if (strncmp(#x, "status", 6) != 0)   \
            {                                    \
                log_error("Expression: %s", #x); \
            }                                    \
            return _tmp_status;                  \
        }                                        \
    } while (0)

#define LOG_RET_VOID(x)                          \
    do                                           \
    {                                            \
        sl_status_t _tmp_status = (x);           \
        LOG_STATUS(_tmp_status);                 \
        if (SL_STATUS_OK != _tmp_status)         \
        {                                        \
            if (strncmp(#x, "status", 6) != 0)   \
            {                                    \
                log_error("Expression: %s", #x); \
            }                                    \
            return;                              \
        }                                        \
    } while (0)

#define UNUSED(x) (void)(x)

void common_init(void);

void common_tick_update(void);

uint32_t core_clock_hz(void);

void delay_ns(uint64_t ns);

void delay_ms(uint32_t ms);

uint32_t time_ms(void);

sl_status_t log_status(const char *file, int line, sl_status_t status);
```


