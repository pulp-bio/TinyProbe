/**
 * @file user.c
 *
 * @brief User main source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup common
 *
 */

#include "user.h"

#include <stdio.h>

#include "common.h"
#include "tp.h"

const osThreadAttr_t user_application_attr = {
    .name = "user_application",
    .priority = (osPriority_t)osPriorityNormal,
    .stack_size = TP_THREAD_STACK_MAIN,
};
osThreadId_t user_application_id;

static void user_application(void *argument);

void user_init(void)
{
    printf("--- Initializing user application ---\r\n");

    common_init();

    user_application_id = osThreadNew(user_application, NULL, &user_application_attr);
    if (user_application_id == NULL)
    {
        printf("!-- Failed to create user application thread --!\r\n");
    }
}

static void user_application(void *argument)
{
    UNUSED(argument);
    sl_status_t status = SL_STATUS_OK;

    status = log_init();
    if (SL_STATUS_OK != status)
    {
        printf("!-- Failed to initialize log: 0x%04lx --!\r\n", status);
        while (1)
            ;
    }

    printf("--- Running user application ---\r\n");

    status = tp_init();
    if (SL_STATUS_OK != status)
    {
        printf("!-- Failed to initialize TinyProbe: 0x%04lx --!\r\n", status);
        while (1)
            ;
    }

    tp_main_thread();
}
