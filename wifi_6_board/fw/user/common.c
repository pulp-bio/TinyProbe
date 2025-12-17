/**
 * @file common.c
 *
 * @brief Common source file
 *
 * @date 17.12.2025
 * @copyright ETH Zurich. All rights reserved.
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

#include "cmsis_os2.h"
#include "os_tick.h"
#include "sl_si91x_clock_manager.h"

osEventFlagsId_t event_flags;
uint32_t _common_ticks_mult = 0;

void common_init(void)
{
    event_flags = osEventFlagsNew(NULL);

    common_tick_update();

    // Enable DWT for nanosecond delay
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void common_tick_update(void)
{
    // Get current System Core clock
    uint32_t __attribute__((unused)) pll_freq = sl_si91x_clock_manager_get_pll_freq(SOC_PLL);

    // TODO: Check if this makes sense
    _common_ticks_mult = 1;
    LOG_D("Core Frequency: %lu MHz", (uint32_t)(pll_freq / 1e6));
}

uint32_t core_clock_hz(void)
{
    return sl_si91x_clock_manager_get_pll_freq(SOC_PLL);
}

void delay_ns(uint64_t ns)
{
    uint64_t cycles = ((uint64_t)ns * (uint64_t)sl_si91x_clock_manager_get_pll_freq(SOC_PLL) + 999999999ULL) / 1000000000ULL;

    if (cycles < 32)
        return;

    // DWT->CYCCNT = 0;

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
