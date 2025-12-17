/**
 * @file tp_mux.c
 *
 * @brief TinyProbe SPI MUX driver source file
 *
 * @date 17.12.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 *
 * @ingroup tinyprobe
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

#include "tp_mux.h"

#include "wius_gpio.h"

wius_gpio_t extintmux_pin = WIUS_GPIO_UULP_OUTPUT(TP_MUX_GPIO_EXTINT);
wius_gpio_t afetxmux_pin = WIUS_GPIO_ULP_OUTPUT(TP_MUX_GPIO_AFETX);

void tp_mux_init(void)
{
    wius_gpio_config(afetxmux_pin);
    wius_gpio_config(extintmux_pin);
}

void tp_mux_select(tp_mux_t mux)
{
    //    wius_gpio_ulp_pin_set(afetxmux_pin, mux & 0b01);
    //    wius_gpio_uulp_pin_set(extintmux_pin, (mux & 0b10) >> 1);
    switch (mux)
    {
    case TP_MUX_PLL:
        wius_gpio_put(extintmux_pin, false);
        wius_gpio_put(afetxmux_pin, false);
        break;
    case TP_MUX_FPGA:
        wius_gpio_put(extintmux_pin, false);
        wius_gpio_put(afetxmux_pin, true);
        break;
    case TP_MUX_AFE:
        wius_gpio_put(extintmux_pin, true);
        wius_gpio_put(afetxmux_pin, false);
        break;
    case TP_MUX_TX:
        wius_gpio_put(extintmux_pin, true);
        wius_gpio_put(afetxmux_pin, true);
        break;
    default:
        break;
    }
}