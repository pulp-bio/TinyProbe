/**
 * @file wius_gpio.h
 *
 * @brief GPIO implementation for WiUS
 *
 * @date 08.09.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup wius
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

/**
 * @brief GPIO output pin definition
 *
 * @param NUM: GPIO pin number
 *
 */
#define WIUS_GPIO_OUTPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_PORT(NUM), _WIUS_GPIO_PIN(NUM)}, GPIO_OUTPUT }

/**
 * @brief ULP GPIO output pin definition
 *
 * @param NUM: GPIO pin number
 *
 */
#define WIUS_GPIO_ULP_OUTPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_ULP_PORT(NUM), _WIUS_GPIO_ULP_PIN(NUM)}, GPIO_OUTPUT }

/**
 * @brief UULP GPIO output pin definition
 *
 * @param NUM: GPIO pin number
 *
 */
#define WIUS_GPIO_UULP_OUTPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_UULP_PORT(NUM), _WIUS_GPIO_UULP_PIN(NUM)}, GPIO_OUTPUT }

/**
 * @brief GPIO input pin definition
 *
 * @param NUM: GPIO pin number
 *
 */
#define WIUS_GPIO_INPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_PORT(NUM), _WIUS_GPIO_PIN(NUM)}, GPIO_INPUT }

/**
 * @brief ULP GPIO input pin definition
 *
 * @param NUM: GPIO pin number
 *
 */
#define WIUS_GPIO_ULP_INPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_ULP_PORT(NUM), _WIUS_GPIO_ULP_PIN(NUM)}, GPIO_INPUT }

/**
 * @brief UULP GPIO input pin definition
 *
 * @param NUM: GPIO pin number
 *
 */
#define WIUS_GPIO_UULP_INPUT(NUM) \
    (wius_gpio_t) { {_WIUS_GPIO_UULP_PORT(NUM), _WIUS_GPIO_UULP_PIN(NUM)}, GPIO_INPUT }

/**
 * @brief GPIO interrupt trigger enumeration
 *
 */
typedef enum wius_gpio_interrupt
{
    WIUS_GPIO_INT_HIGH = SL_GPIO_INTERRUPT_HIGH,            /**< High level */
    WIUS_GPIO_INT_LOW = SL_GPIO_INTERRUPT_LOW,              /**< Low level */
    WIUS_GPIO_INT_RISING = SL_GPIO_INTERRUPT_RISING_EDGE,   /**< Rising edge */
    WIUS_GPIO_INT_FALLING = SL_GPIO_INTERRUPT_FALLING_EDGE, /**< Falling edge */
    WIUS_GPIO_INT_TOGGLE = SL_GPIO_INTERRUPT_RISE_FALL_EDGE /**< Any edge */
} wius_gpio_interrupt_t;

typedef sl_si91x_gpio_pin_config_t wius_gpio_t;
typedef sl_gpio_irq_callback_t wius_gpio_callback_t;

// TODO: Fill in the return values for the functions below

/**
 * @brief Initialize GPIO module
 *
 */
sl_status_t wius_gpio_init(void);

/**
 * @brief Configure GPIO pin
 *
 * @param gpio: GPIO pin definition
 *
 * @note Must be called before using the pin
 * @note Must be called after @ref wius_gpio_init
 *
 */
sl_status_t wius_gpio_config(wius_gpio_t gpio);

/**
 * @brief Attach interrupt to GPIO pin
 *
 * @param gpio: GPIO pin definition
 * @param trigger: Interrupt trigger (see @ref wius_gpio_interrupt_t)
 * @param function: Interrupt callback function
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_INVALID_STATE: Pin is not an input or maximum number of interrupts reached
 *
 */
sl_status_t wius_gpio_attach_interrupt(wius_gpio_t gpio, wius_gpio_interrupt_t trigger, wius_gpio_callback_t function);

/**
 * @brief Set GPIO pin state
 *
 * @param gpio: GPIO pin definition
 * @param on: State to set (true = high, false = low)
 *
 */
void wius_gpio_put(wius_gpio_t gpio, bool on);

/**
 * @brief Toggle GPIO pin state
 *
 * @param gpio: GPIO pin definition
 *
 */
void wius_gpio_toggle(wius_gpio_t gpio);

/**
 * @brief Get GPIO pin state
 *
 * @param gpio: GPIO pin definition
 *
 * @return GPIO pin state (0 = low, 1 = high)
 *
 */
uint8_t wius_gpio_get(wius_gpio_t gpio);