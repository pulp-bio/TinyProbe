

# File led.c

[**File List**](files.md) **>** [**common**](dir_85edcc1f099af2a701a791767791d401.md) **>** [**led.c**](led_8c.md)

[Go to the documentation of this file](led_8c.md)


```C++

#include "led.h"

#include "wius_gpio.h"

sl_status_t led_init(void)
{
    LOG_RET_STATUS(wius_gpio_config(LED_GPIO_RED));
    LOG_RET_STATUS(wius_gpio_config(LED_GPIO_GREEN));
#ifdef LED_GPIO_BLUE
    LOG_RET_STATUS(wius_gpio_config(LED_GPIO_BLUE));
    wius_gpio_put(LED_GPIO_BLUE, LED_INVERTED); // Ensure blue LED is off if it exists
#endif
    led_set(LED_COLOR_OFF);
    return SL_STATUS_OK;
}

sl_status_t led_set(uint8_t x)
{
    switch (x)
    {
    case LED_COLOR_OFF:
        wius_gpio_put(LED_GPIO_RED, LED_INVERTED);
        wius_gpio_put(LED_GPIO_GREEN, LED_INVERTED);
        break;
    case LED_COLOR_RED:
        wius_gpio_put(LED_GPIO_RED, !LED_INVERTED);
        wius_gpio_put(LED_GPIO_GREEN, LED_INVERTED);
        break;
    case LED_COLOR_GREEN:
        wius_gpio_put(LED_GPIO_RED, LED_INVERTED);
        wius_gpio_put(LED_GPIO_GREEN, !LED_INVERTED);
        break;
    case LED_COLOR_YELLOW:
        wius_gpio_put(LED_GPIO_RED, !LED_INVERTED);
        wius_gpio_put(LED_GPIO_GREEN, !LED_INVERTED);
        break;
    default:
        log_error("Invalid LED color: %u", x);
        return SL_STATUS_INVALID_PARAMETER;
    }

    return SL_STATUS_OK;
}
```


