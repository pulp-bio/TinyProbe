/**
 * @file log.h
 *
 * @brief Logging header file
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

#ifndef _LOG_H_
#define _LOG_H_

#include <stdarg.h>
#include <stdbool.h>

#ifndef LOG_MAX_CALLBACKS
#define LOG_MAX_CALLBACKS 2
#endif

#ifndef LOG_BUFFER_SIZE
#define LOG_BUFFER_SIZE 128
#endif

typedef enum log_level_e
{
    TRACE = 0,
    DEBUG = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
    FATAL = 5,
    LOG_LEVEL_COUNT,
} log_level_t;

typedef int (*log_callback_t)(const char *str, int len);

extern const char *log_level_strings[LOG_LEVEL_COUNT];

bool log_register_callback(log_callback_t callback);
#ifndef LOG_ONCE
bool log_unregister_callback(log_callback_t callback);
#endif // LOG_ONCE

#define _LOG_LOG(level, fmt, ...) log_log(level, __FILE_NAME__, __FUNCTION__, __LINE__, fmt, ##__VA_ARGS__)
void log_log(log_level_t level, const char *file, const char *function, int line, const char *fmt, ...);

#define log_trace(fmt, ...) _LOG_LOG(TRACE, fmt, ##__VA_ARGS__)
#define log_debug(fmt, ...) _LOG_LOG(DEBUG, fmt, ##__VA_ARGS__)
#define log_info(fmt, ...) _LOG_LOG(INFO, fmt, ##__VA_ARGS__)
#define log_warn(fmt, ...) _LOG_LOG(WARN, fmt, ##__VA_ARGS__)
#define log_error(fmt, ...) _LOG_LOG(ERROR, fmt, ##__VA_ARGS__)
#define log_fatal(fmt, ...) _LOG_LOG(FATAL, fmt, ##__VA_ARGS__)
#ifdef LOG_IMPLEMENTATION

#include <stdio.h>

static log_callback_t log_callbacks[LOG_MAX_CALLBACKS] = {0};
static int log_callback_count = 0;
static char log_buffer[LOG_BUFFER_SIZE];
const char *log_level_strings[LOG_LEVEL_COUNT] = {
    "TRC",
    "DEB",
    "INF",
    "WRN",
    "ERR",
    "FTL",
};
#ifndef LOG_NO_COLOR
static const char *log_level_colors[LOG_LEVEL_COUNT] = {
    "\x1b[36m", // Cyan for TRACE
    "\x1b[34m", // Blue for DEBUG
    "\x1b[32m", // Green for INFO
    "\x1b[33m", // Yellow for WARN
    "\x1b[31m", // Red for ERROR
    "\x1b[35m", // Magenta for FATAL
};
#define LOG_STYLE_BOLD "\x1b[1m"
#define LOG_STYLE_DIM "\x1b[2m"
#define LOG_STYLE_RESET "\x1b[0m"
#endif

bool log_register_callback(log_callback_t callback)
{
    if (log_callback_count >= LOG_MAX_CALLBACKS)
    {
        return false;
    }
    log_callbacks[log_callback_count++] = callback;
    return true;
}

#ifndef LOG_ONCE
bool log_unregister_callback(log_callback_t callback)
{
    for (int i = 0; i < log_callback_count; i++)
    {
        log_callback_t cb = log_callbacks[i];

        if (cb == callback)
        {
            for (int j = i; j < log_callback_count - 1; j++)
            {
                log_callbacks[j] = log_callbacks[j + 1];
            }
            log_callback_count--;

            return true;
        }
    }

    return false;
}
#endif // LOG_ONCE

void log_log(log_level_t level, const char *file, const char *function, int line, const char *fmt, ...)
{
    // #ifndef LOG_NO_COLOR
    // int written = snprintf(log_buffer, LOG_BUFFER_SIZE, "%s%s(%s)%s %s[%s:%d] %s:%s ", log_level_colors[level], LOG_STYLE_BOLD, log_level_strings[level], LOG_STYLE_RESET, LOG_STYLE_DIM, file, line, function, LOG_STYLE_RESET);
    // #else
    (void)file;
    (void)function;
    (void)line;
    int written = snprintf(log_buffer, LOG_BUFFER_SIZE, "(%s) ", log_level_strings[level]);
    // #endif

    if (log_callback_count == 0)
    {
        return;
    }

    va_list args;
    va_start(args, fmt);
    written += vsnprintf(log_buffer + written, LOG_BUFFER_SIZE - written, fmt, args);
    va_end(args);

    if (written < LOG_BUFFER_SIZE - 2)
    {
        log_buffer[written++] = '\n';
        log_buffer[written] = '\0';
    }
    else
    {
        log_buffer[LOG_BUFFER_SIZE - 2] = '\n';
        log_buffer[LOG_BUFFER_SIZE - 1] = '\0';
        written = LOG_BUFFER_SIZE;
    }

    for (int i = 0; i < log_callback_count; i++)
    {
        log_callbacks[i](log_buffer, written);
    }
}

#endif // LOG_IMPLEMENTATION

#endif // _LOG_H_
