/**
 * @file common.h
 *
 * @brief Common header file
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

#pragma once

// === Common Header Files ===
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "sl_status.h"

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

#define GET(args, type, pos) (*(type *)(args + pos)) // Get value of given type from args at given position

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
 * @brief Get the current core clock in Hz
 *
 * @return Current core clock in Hz
 *
 */
uint32_t core_clock_hz(void);

/**
 * @brief Delay for a given number of nanoseconds
 *
 * @param ns Number of nanoseconds to delay
 *
 * @note This function is not very accurate
 *
 */
void delay_ns(uint64_t ns);

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
