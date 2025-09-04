/**
 * @file common.h
 *
 * @brief Common header file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup common
 *
 */

#pragma once

// === Common Header Files ===
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "sl_status.h"
#include "cmsis_os2.h"
#include "os_tick.h"

#include "config.h"
#include "log.h"

#define CONCAT_2(a, b) a##b
#define CONCAT_3(a, b, c) a##b##c

#define TICKS_PER_SEC (OS_Tick_GetClock() / OS_Tick_GetInterval()) // Number of ticks per second

#define CHECK_STATUS(x)             \
    do                              \
    {                               \
        status = (x);               \
        if (SL_STATUS_OK != status) \
            return status;          \
    } while (0) // Check status and return if not OK

#define UNUSED(x) (void)(x) // Suppress unused variable warning

/**
 * @brief Initialize some common stuff
 *
 */
void common_init(void);

/**
 * @brief Update the common tick
 *
 */
void common_tick_update(void);

/**
 * @brief Delay for a given number of nanoseconds
 *
 * @param ns Number of nanoseconds to delay
 *
 * @note This function is not very accurate
 *
 */
void delay_ns(uint32_t ns);

/**
 * @brief Delay for a given number of milliseconds
 *
 * @param us Number of milliseconds to delay
 *
 */
void delay_ms(uint32_t ms);

/**
 * @brief Get the current time in milliseconds
 *
 * @return Current time in milliseconds
 *
 */
uint32_t time_ms(void);