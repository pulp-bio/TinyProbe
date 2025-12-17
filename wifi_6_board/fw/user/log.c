/**
 * @file log.c
 *
 * @brief Logging source file
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

#include "log.h"

#include <stdio.h>
#include <stdarg.h>

#include "cmsis_os2.h"
#include "sl_iostream.h"

osMutexId_t log_mutex;
// int _log_lost = 0;

char buffer[WIUS_LOG_BUFFER_SIZE];

sl_status_t log_init(void)
{
    log_mutex = osMutexNew(NULL);
    if (log_mutex == NULL)
    {
        printf("!-- Failed to create log mutex --!\r\n");
        return SL_STATUS_FAIL;
    }

    return SL_STATUS_OK;
}

void _log_printf(const char *level, uint32_t tick_count, const char *function, const char *format, ...)
{
    (void)tick_count; // Unused for now
    (void)function;   // Unused for now

    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);

    //    if (osMutexAcquire(log_mutex, 100) != osOK)
    //    {
    ////        _log_lost++;
    //        return;
    //    }

    //    if (_log_lost)
    //    {
    //        printf("!-- %d log messages lost --!\r\n", _log_lost);
    //        _log_lost = 0;
    //    }

    // printf("[%s %7lu %27s]   %s\r\n", level, tick_count, function, buffer);
    printf("[%s]   %s\r\n", level, buffer);
    // sl_iostream_printf(SL_IOSTREAM_STDOUT, "[%s]   %s\r\n", level, buffer);

    //    osMutexRelease(log_mutex);
}
