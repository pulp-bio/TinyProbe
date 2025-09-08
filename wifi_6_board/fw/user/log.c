/**
 * @file log.c
 *
 * @brief Logging source file
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

#include "log.h"

#include <stdio.h>
#include <stdarg.h>

#include "cmsis_os2.h"

osMutexId_t log_mutex;
int _log_lost = 0;

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
    if (osMutexAcquire(log_mutex, 100) != osOK)
    {
        _log_lost++;
        return;
    }

    if (_log_lost)
    {
        printf("!-- %d log messages lost --!\r\n", _log_lost);
        _log_lost = 0;
    }

    va_list args;
    va_start(args, format);

    printf("[%s %7lu %27s]   ", level, tick_count, function);
    vprintf(format, args);
    printf("\r\n");

    va_end(args);

    osMutexRelease(log_mutex);
}