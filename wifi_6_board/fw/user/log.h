/**
 * @file log.h
 *
 * @brief Logging header file
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

#include <stdio.h>

#include "sys.h"
#include "cmsis_os2.h"
#include "os_tick.h"
#include "sl_status.h"

#include "config.h"

//! Log everything
#define LOG_LEVEL_DEBUG 3
//! Log only information
#define LOG_LEVEL_INFO 2
//! Log warnings and errors
#define LOG_LEVEL_WARNING 1
//! Log only errors
#define LOG_LEVEL_ERROR 0

#ifdef WIUS_LOG_LEVEL
//! Use WiUS log level if defined
#define LOG_LEVEL WIUS_LOG_LEVEL
#endif

#ifndef LOG_LEVEL
//! Default log level
#define LOG_LEVEL LOG_LEVEL_DEBUG
#endif

//! Log a debug message
#if LOG_LEVEL >= LOG_LEVEL_DEBUG
#define LOG_D(...) _LOG_PRINT("DEB", __VA_ARGS__)
#else
#define LOG_D(...)
#endif

//! Log an info message
#if LOG_LEVEL >= LOG_LEVEL_INFO
#define LOG_I(...) _LOG_PRINT("INF", __VA_ARGS__)
#else
#define LOG_I(...)
#endif

//! Log a warning message
#if LOG_LEVEL >= LOG_LEVEL_WARNING
#define LOG_W(...) _LOG_PRINT("WRN", __VA_ARGS__)
#else
#define LOG_W(...)
#endif

//! Log an error message
#if LOG_LEVEL >= LOG_LEVEL_ERROR
#define LOG_E(...) _LOG_PRINT("ERR", __VA_ARGS__)
#else
#define LOG_E(...)
#endif

//! Assert macro
#define ASSERT(x, ...) _LOG_ASSERT(x, #x, ##__VA_ARGS__)

#define _LOG_ASSERT(x, x_str, ...)                                  \
    do                                                              \
    {                                                               \
        if (!(x))                                                   \
        {                                                           \
            printf("\n");                                           \
            LOG_E("Assertion failed: " x_str "\n\r\t" __VA_ARGS__); \
            while (true)                                            \
            {                                                       \
            }                                                       \
        }                                                           \
    } while (false)

#define _LOG_PRINT(level, ...) _log_printf(level, osKernelGetTickCount(), __func__, __VA_ARGS__)

/**
 * @brief Initialize the logging system
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Failure (Mutex creation failed)
 *
 */
sl_status_t log_init(void);

void _log_printf(const char *level, uint32_t tick_count, const char *function, const char *format, ...);
