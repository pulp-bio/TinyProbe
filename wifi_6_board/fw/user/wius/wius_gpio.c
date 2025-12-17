/**
 * @file wius_gpio.c
 *
 * @brief WiUS GPIO implementation source file
 *
 * @date 17.12.2025
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

#include "wius_gpio.h"

static uint32_t _wius_gpio_active_interrupts = 0;
static uint32_t _wius_gpio_ulp_active_interrupts = 0;
static uint32_t _wius_gpio_uulp_active_interrupts = 0;

sl_status_t wius_gpio_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    CHECK_STATUS(sl_gpio_driver_init());

    return status;
}

sl_status_t wius_gpio_config(wius_gpio_t gpio)
{
    sl_status_t status = SL_STATUS_OK;

    CHECK_STATUS(sl_gpio_set_configuration(gpio));

    if ((gpio.port_pin.port == SL_GPIO_UULP_PORT) && (gpio.direction == GPIO_INPUT))
    {
        uulp_pad_config_t uulp_pad = {
            .gpio_padnum = gpio.port_pin.pin,
            .pad_select = 1,
            .mode = 0,
            .direction = 1,
            .receiver = 1,
        };

        CHECK_STATUS(sl_si91x_gpio_driver_set_uulp_pad_configuration(&uulp_pad));
    }

    return status;
}

sl_status_t wius_gpio_attach_interrupt(wius_gpio_t gpio, wius_gpio_interrupt_t trigger, wius_gpio_callback_t function)
{
    sl_status_t status = SL_STATUS_OK;

    uint32_t *interrupt_number = &_wius_gpio_active_interrupts;
    if (gpio.port_pin.port == SL_GPIO_ULP_PORT)
    {
        interrupt_number = &_wius_gpio_ulp_active_interrupts;
    }
    else if (gpio.port_pin.port == SL_GPIO_UULP_PORT)
    {
        interrupt_number = &_wius_gpio_uulp_active_interrupts;
    }

    // CHECK_STATUS(sl_gpio_driver_configure_interrupt((sl_gpio_t *)&gpio.port_pin, *interrupt_number, (sl_gpio_interrupt_flag_t)trigger, function, NULL));
    // TODO: Check what to pass as int_no
    uint32_t avl_intr_no = 0;
    CHECK_STATUS(sl_gpio_driver_configure_interrupt(&gpio.port_pin, 2, (sl_gpio_interrupt_flag_t)trigger, function, &avl_intr_no));
    LOG_D("avl_intr_no: %lu", avl_intr_no);
    *interrupt_number += 1;

    return status;
}

void wius_gpio_put(wius_gpio_t gpio, bool on)
{
    on ? sl_gpio_driver_set_pin((sl_gpio_t *)&gpio) : sl_gpio_driver_clear_pin((sl_gpio_t *)&gpio);
}

void wius_gpio_toggle(wius_gpio_t gpio)
{
    sl_gpio_driver_toggle_pin((sl_gpio_t *)&gpio);
}

uint8_t wius_gpio_get(wius_gpio_t gpio)
{
    uint8_t result = 0;
    sl_gpio_driver_get_pin((sl_gpio_t *)&gpio, &result);
    return result;
}
