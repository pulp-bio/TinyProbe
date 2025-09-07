/**
 * @file tp_mux.c
 *
 * @brief SPI MUX driver for TinyProbe source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
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