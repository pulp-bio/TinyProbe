/**
 * @file common.c
 *
 * @brief Common source file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup common
 *
 * @parblock
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * @endparblock
 *
 */

#include "common.h"

#include "os_tick.h"
#include "sl_si91x_clock_manager.h"
#include "SEGGER_RTT.h"

#include "log.h"

uint32_t _common_ticks_mult = 0;
static uint32_t _common_core_clock_hz = 0;

int _log_callback(const char *str, int len)
{
    return SEGGER_RTT_Write(0, str, len);
}

void common_init(void)
{
    common_tick_update();

    log_register_callback(_log_callback);

    led_init();

    // Enable DWT for nanosecond delay
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void common_tick_update(void)
{
    // Get current System Core clock
    _common_core_clock_hz = sl_si91x_clock_manager_get_pll_freq(SOC_PLL);

    // TODO: Update this to work over different clock frequencies
    _common_ticks_mult = 1;
    log_trace("Core Frequency: %lu MHz", (uint32_t)(_common_core_clock_hz / 1000000));
}

uint32_t core_clock_hz(void)
{
    return _common_core_clock_hz;
}

void delay_ns(uint64_t ns)
{
    if (ns == 0)
        return;

    uint64_t cycles = (ns * (uint64_t)_common_core_clock_hz + 999999999ULL) / 1000000000ULL;

    if (cycles < 32)
        return;

    // Account for function/loop overhead (~20–40 cycles typical). Tune for your build.
    const uint64_t overhead = 32;
    uint32_t start = DWT->CYCCNT;
    while ((uint64_t)(DWT->CYCCNT - start) < (uint64_t)(cycles + overhead))
    {
        if (DWT->CYCCNT < start)
            return;
    }
}

void delay_ms(uint32_t ms)
{
    osDelay(ms * _common_ticks_mult);
}

uint32_t time_ms(void)
{
    return osKernelGetTickCount() / _common_ticks_mult;
}

sl_status_t log_status(const char *file, int line, sl_status_t status)
{
    if (SL_STATUS_OK == status)
    {
        // log_trace("OK at %s:%d", file, line);
    }
    else
    {
        log_error("Error at %s:%d: 0x%04lx", file, line, status);
    }

    return status;
}
