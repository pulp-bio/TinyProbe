

# File wius\_gpio.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_gpio.h**](wius__gpio_8h.md)

[Go to the documentation of this file](wius__gpio_8h.md)


```C++

#pragma once

#include "common.h"

#include "sl_gpio_board.h"
#include "sl_si91x_driver_gpio.h"

#define _WIUS_GPIO_PIN(num) num
#define _WIUS_GPIO_PORT(num) SL_GPIO_PORT_A // See https://github.com/SiliconLabs/wiseconnect/tree/9f6db891b349369a45da7d66f53f9cd83d3ba260/examples/si91x_soc/peripheral/sl_si91x_gpio_detailed_example#:~:text=NOTE%20%3A%20There%20is%20also%20option%20to%20select%20(0%2D57)%20pins%20with%20SL_GPIO_PORT_A.%20For%20example%2C%20to%20select%20HP%20GPIO%20pin%20number%2049%2C%20one%20can%20select%20Port%20as%20SL_GPIO_PORT_A%20and%20pin%20number%20as%2049.%20This%20option%20is%20given%20only%20when%20SL_GPIO_PORT_A%20GPIO%20port%20is%20selected.%20(57%2D63)pins%20are%20reserved.

#define _WIUS_GPIO_ULP_PIN(num) num
#define _WIUS_GPIO_ULP_PORT(num) SL_GPIO_ULP_PORT

#define _WIUS_GPIO_UULP_PIN(num) num
#define _WIUS_GPIO_UULP_PORT(num) SL_GPIO_UULP_PORT

#define WIUS_GPIO_OUTPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_PORT(NUM), _WIUS_GPIO_PIN(NUM)}, GPIO_OUTPUT }

#define WIUS_GPIO_ULP_OUTPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_ULP_PORT(NUM), _WIUS_GPIO_ULP_PIN(NUM)}, GPIO_OUTPUT }

#define WIUS_GPIO_UULP_OUTPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_UULP_PORT(NUM), _WIUS_GPIO_UULP_PIN(NUM)}, GPIO_OUTPUT }

#define WIUS_GPIO_INPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_PORT(NUM), _WIUS_GPIO_PIN(NUM)}, GPIO_INPUT }

#define WIUS_GPIO_ULP_INPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_ULP_PORT(NUM), _WIUS_GPIO_ULP_PIN(NUM)}, GPIO_INPUT }

#define WIUS_GPIO_UULP_INPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_UULP_PORT(NUM), _WIUS_GPIO_UULP_PIN(NUM)}, GPIO_INPUT }

typedef enum wius_gpio_interrupt
{
    WIUS_GPIO_INT_HIGH = SL_GPIO_INTERRUPT_HIGH,            
    WIUS_GPIO_INT_LOW = SL_GPIO_INTERRUPT_LOW,              
    WIUS_GPIO_INT_RISING = SL_GPIO_INTERRUPT_RISING_EDGE,   
    WIUS_GPIO_INT_FALLING = SL_GPIO_INTERRUPT_FALLING_EDGE, 
    WIUS_GPIO_INT_TOGGLE = SL_GPIO_INTERRUPT_RISE_FALL_EDGE 
} wius_gpio_interrupt_t;

typedef sl_si91x_gpio_pin_config_t wius_gpio_t;
typedef sl_gpio_irq_callback_t wius_gpio_callback_t;

sl_status_t wius_gpio_init(void);

sl_status_t wius_gpio_config(wius_gpio_t gpio);

sl_status_t wius_gpio_attach_interrupt(wius_gpio_t gpio, wius_gpio_interrupt_t trigger, wius_gpio_callback_t function);

void wius_gpio_put(wius_gpio_t gpio, bool on);

void wius_gpio_toggle(wius_gpio_t gpio);

uint8_t wius_gpio_get(wius_gpio_t gpio);
```


