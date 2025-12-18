/**
 * @file common.h
 *
 * @brief Common header file
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

#pragma once

// === Common Header Files ===
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "sl_status.h"

#include "config.h"
#include "log.h"

//! Concatenate two tokens
#define CONCAT_2(a, b) a##b
//! Concatenate three tokens
#define CONCAT_3(a, b, c) a##b##c

//! Number of RTOS ticks per second
#define TICKS_PER_SEC (OS_Tick_GetClock() / OS_Tick_GetInterval())

/**
 * @brief Macro to check the status of a function call and return if it is not SL_STATUS_OK
 *
 * @param x: Function call to check
 *
 * @warning This macro uses 'return', so it can only be used in functions with a return value of sl_status_t and a variable named 'status'
 *
 */
#define CHECK_STATUS(x)                                                 \
    do                                                                  \
    {                                                                   \
        status = (x);                                                   \
        if (SL_STATUS_OK != status)                                     \
        {                                                               \
            LOG_E("Error at %s:%d: 0x%lx", __FILE__, __LINE__, status); \
            return status;                                              \
        }                                                               \
    } while (0)

//! Suppress unused variable warning
#define UNUSED(x) (void)(x)

/**
 * @brief Macro to get a typed argument from a byte array
 *
 * @param args: Pointer to the byte array
 * @param type: Type of the argument to get
 * @param pos: Position of the argument in the byte array
 *
 * @return The argument casted to the specified type
 *
 * @note The position is in bytes
 * @note The caller is responsible for ensuring that the position is valid and that the type matches the data at that position
 *
 * @warning This macro does not perform any bounds checking
 *
 */
#define GET(args, type, pos) (*(type *)(args + pos))

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
 * @param ms Number of milliseconds to delay
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
