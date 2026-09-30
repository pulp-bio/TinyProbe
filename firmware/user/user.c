/**
 * @file user.c
 *
 * @brief User main source file
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
    common_init();

    led_set(LED_COLOR_YELLOW);

    printf("--- Initializing user application ---\r\n");

    user_application_id = osThreadNew(user_application, NULL, &user_application_attr);
    if (user_application_id == NULL)
    {
        printf("!-- Failed to create user application thread --!\r\n");
        led_set(LED_COLOR_RED);
    }
}

static void user_application(void *argument)
{
    printf("--- Running user application ---\r\n");

    UNUSED(argument);

    sl_status_t status = SL_STATUS_OK;

    status = tp_init();
    if (SL_STATUS_OK != status)
    {
        printf("!-- Failed to initialize TinyProbe: 0x%04lx --!\r\n", status);
        led_set(LED_COLOR_RED);
        while (1)
            ;
    }

    led_set(LED_COLOR_GREEN);

    status = tp_main_thread();
    if (SL_STATUS_OK != status)
    {
        printf("!-- Failed to run TinyProbe main thread: 0x%04lx --!\r\n", status);
        led_set(LED_COLOR_RED);
    }

    printf("--- User application terminated with status 0x%04lx ---\r\n", status);
    led_set(LED_COLOR_YELLOW);
}
