/**
 * @file tp_power.c
 *
 * @brief Power Management driver for TinyProbe source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
 *
 */

#include "tp_power.h"

// #include "sl_gpio_board.h"

#include "wius_gpio.h"

wius_gpio_t neg_5v_pin = WIUS_GPIO_ULP_OUTPUT(TP_POWER_GPIO_NEG_5V);
wius_gpio_t neg_hv_pin = WIUS_GPIO_OUTPUT(TP_POWER_GPIO_NEG_HV);
wius_gpio_t pos_hv_pin = WIUS_GPIO_OUTPUT(TP_POWER_GPIO_POS_HV);
wius_gpio_t lvds_pwr_switch_pin = WIUS_GPIO_ULP_OUTPUT(TP_POWER_GPIO_LVDS_PWR_SW);

void tp_power_init(void)
{
    wius_gpio_config(neg_5v_pin);
    wius_gpio_config(neg_hv_pin);
    wius_gpio_config(pos_hv_pin);
    wius_gpio_config(lvds_pwr_switch_pin);

    // Set all pins to low initially
    wius_gpio_put(neg_5v_pin, false);
    wius_gpio_put(neg_hv_pin, false);
    wius_gpio_put(pos_hv_pin, false);
    wius_gpio_put(lvds_pwr_switch_pin, false);
}

void tp_power_on(void)
{
    wius_gpio_put(pos_hv_pin, true);
    wius_gpio_put(neg_hv_pin, true);
    delay_ms(100);
    wius_gpio_put(neg_5v_pin, true);
    delay_ms(100);
}

void tp_power_set(tp_power_domain_t domain, bool enabled)
{
    switch (domain)
    {
    case TP_POWER_DOMAIN_LVDS_2_5V:
        wius_gpio_put(lvds_pwr_switch_pin, enabled);
        // LOG_D("Changing LVDS pin to %u", enabled);
        // LOG_D("Pin is at %u", wius_gpio_get(lvds_pwr_switch_pin));
        break;
    case TP_POWER_DOMAIN_POS_HV:
        wius_gpio_put(pos_hv_pin, enabled);
        // LOG_D("Changing +HV pin to %u", enabled);
        // LOG_D("Pin is at %u", wius_gpio_get(pos_hv_pin));
        break;
    case TP_POWER_DOMAIN_NEG_HV:
        wius_gpio_put(neg_hv_pin, enabled);
        // LOG_D("Changing -HV pin to %u", enabled);
        // LOG_D("Pin is at %u", wius_gpio_get(neg_hv_pin));
        break;
    case TP_POWER_DOMAIN_NEG_5V:
        wius_gpio_put(neg_5v_pin, enabled);
        // LOG_D("Changing -5V pin to %u", enabled);
        // LOG_D("Pin is at %u", wius_gpio_get(neg_5v_pin));
        break;
    case TP_POWER_DOMAIN_PLL_PWD:
        // TODO
        // LOG_D("Changing PLL pin to %u", enabled);
        //    LOG_D("Pin is at %u", wius_gpio_ulp_pin_get(lvds_pwr_switch_pin));
        LOG_W("Not implemented");
        break;
    default:
        return;
    }
}