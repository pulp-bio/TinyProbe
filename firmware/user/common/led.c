/**
 * @file led.c
 *
 * @brief LED control implementation file
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
