

# File user.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**user.c**](user_8c.md)

[Go to the documentation of this file](user_8c.md)


```C++

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
```


