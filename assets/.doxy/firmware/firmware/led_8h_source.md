

# File led.h

[**File List**](files.md) **>** [**common**](dir_85edcc1f099af2a701a791767791d401.md) **>** [**led.h**](led_8h.md)

[Go to the documentation of this file](led_8h.md)


```C++

#pragma once

#include "config.h"

#define LED_COLOR_OFF 0
#define LED_COLOR_RED 1
#define LED_COLOR_GREEN 2
#define LED_COLOR_YELLOW 3

#ifndef WIUS_BOARD
#warning "No WIUS_BOARD defined, LED functions will be stubbed"
#define led_init() (SL_STATUS_OK)
#define led_set(x) (SL_STATUS_OK)
#else
#include "sl_status.h"

#if WIUS_BOARD == 0
#define LED_GPIO_RED WIUS_GPIO_OUTPUT(50)
#define LED_GPIO_GREEN WIUS_GPIO_OUTPUT(51)
#define LED_GPIO_BLUE WIUS_GPIO_OUTPUT(15)
#define LED_INVERTED true // LEDs are active low on DK2605A
#elif WIUS_BOARD == 1
#define LED_GPIO_RED WIUS_GPIO_OUTPUT(10)
#define LED_GPIO_GREEN WIUS_GPIO_ULP_OUTPUT(2)
#define LED_INVERTED true // LEDs are active low on EK2708A
#elif WIUS_BOARD == 2
#define LED_GPIO_RED WIUS_GPIO_ULP_OUTPUT(2)
#define LED_GPIO_GREEN WIUS_GPIO_OUTPUT(10)
#define LED_INVERTED true // LEDs are active low on PK6031A
#elif WIUS_BOARD == 3
#define LED_GPIO_RED WIUS_GPIO_OUTPUT(7)
#define LED_GPIO_GREEN WIUS_GPIO_OUTPUT(6)
#define LED_INVERTED true // LEDs are active low on WIUS1
#else
#error "Unknown WIUS_BOARD"
#endif

sl_status_t led_init(void);

sl_status_t led_set(uint8_t x);
#endif
```


