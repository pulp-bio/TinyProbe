/**
 * @file led.h
 *
 * @brief LED control header file
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

/**
 * @brief Initialize the LED(s)
 *
 * @return SL_STATUS_OK if successful, otherwise an error code
 */
sl_status_t led_init(void);

/**
 * @brief Set the state of the LED(s)
 *
 * @param x: Color to set
 *
 * @return SL_STATUS_OK if successful, otherwise an error code
 */
sl_status_t led_set(uint8_t x);
#endif
