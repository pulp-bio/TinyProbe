/**
 * @file log.c
 *
 * @brief Logging source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup common
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