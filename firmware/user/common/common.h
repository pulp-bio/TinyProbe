/**
 * @file common.h
 *
 * @brief Common header file
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

//! Concatenate two tokens
#define CONCAT_2(a, b) a##b
//! Concatenate three tokens
#define CONCAT_3(a, b, c) a##b##c

//! Number of RTOS ticks per second
#define TICKS_PER_SEC (OS_Tick_GetClock() / OS_Tick_GetInterval())

/**
 * @brief Macro to log the status of a function call with file and line information
 *
 * @param status: Status to log
 *
 */
#define LOG_STATUS(status) log_status(__FILE__, __LINE__, (status))

/**
 * @brief Macro to check the status of a function call and return if it is not `SL_STATUS_OK`
 *
 * @param x: Function call to check
 *
 * @warning This macro returns with `sl_status_t`
 *
 */
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

/**
 * @brief Macro to check the status of a function call and return if it is not `SL_STATUS_OK`
 *
 * @param x: Function call to check
 *
 * @warning This macro returns with `void`
 *
 */
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

//! Suppress unused variable warning
#define UNUSED(x) (void)(x)

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

/**
 * @brief Log an error message with file and line information
 *
 * @param file File name
 * @param line Line number
 * @param status Status to log
 *
 * @return Propagated status
 *
 */
sl_status_t log_status(const char *file, int line, sl_status_t status);
