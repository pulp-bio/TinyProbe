/**
 * @file common.c
 *
 * @brief Common source file
 *
 * @date 08.09.2025
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

#include "sl_si91x_clock_manager.h"

osEventFlagsId_t event_flags;
uint32_t _common_ticks_mult = 0;

void common_init(void)
{
    event_flags = osEventFlagsNew(NULL);

    common_tick_update();
}

void common_tick_update(void)
{
    // Get current System Core clock
    uint32_t __attribute__((unused)) pll_freq = sl_si91x_clock_manager_get_pll_freq(SOC_PLL);

    // TODO: Check if this makes sense
    _common_ticks_mult = 1;
    LOG_D("Core Frequency: %lu MHz", (uint32_t)(pll_freq / 1e6));
}

// TODO: Implement a more accurate delay function
void delay_ns(uint32_t ns)
{
    // volatile int32_t timeout = (ns - 110000) * 119 / 1000 / 7;
    // //  volatile int32_t timeout = ns * 100 / 1000 / 7;

    // do
    // {
    //     timeout--;
    // } while (timeout > 0);

    // //  delay_ms(2 + ns / 1000000);
    delay_ms(ns / 1000000 + 1);
}

void delay_ms(uint32_t ms)
{
    osDelay(ms * _common_ticks_mult);
}

uint32_t time_ms(void)
{
    return osKernelGetTickCount() / _common_ticks_mult;
}
