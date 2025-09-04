/**
 * @file log.h
 *
 * @brief Logging header file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup common
 *
 */

#pragma once

#include <stdio.h>

#include "sys.h"
#include "cmsis_os2.h"
#include "os_tick.h"
#include "sl_status.h"

#include "config.h"

#define LOG_LEVEL_DEBUG 3   // Log everything
#define LOG_LEVEL_INFO 2    // Log only information
#define LOG_LEVEL_WARNING 1 // Log warnings and errors
#define LOG_LEVEL_ERROR 0   // Log only errors

#ifdef WIUS_LOG_LEVEL
#define LOG_LEVEL WIUS_LOG_LEVEL
#endif

#ifndef LOG_LEVEL
#define LOG_LEVEL LOG_LEVEL_DEBUG
#endif

#if LOG_LEVEL >= LOG_LEVEL_DEBUG
#define LOG_D(...) _LOG_PRINT("DEB", __VA_ARGS__) // Debug message
#else
#define LOG_D(...)
#endif

#if LOG_LEVEL >= LOG_LEVEL_INFO
#define LOG_I(...) _LOG_PRINT("INF", __VA_ARGS__) // Info message
#else
#define LOG_I(...)
#endif

#if LOG_LEVEL >= LOG_LEVEL_WARNING
#define LOG_W(...) _LOG_PRINT("WRN", __VA_ARGS__) // Warning message
#else
#define LOG_W(...)
#endif

#if LOG_LEVEL >= LOG_LEVEL_ERROR
#define LOG_E(...) _LOG_PRINT("ERR", __VA_ARGS__) // Error message
#else
#define LOG_E(...)
#endif

#define ASSERT(x, ...) _LOG_ASSERT(x, #x, ##__VA_ARGS__) // Assert macro

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

sl_status_t log_init(void);
void _log_printf(const char *level, uint32_t tick_count, const char *function, const char *format, ...);
