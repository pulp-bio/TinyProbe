/**
 * @file common.c
 *
 * @brief Common source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup common
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
