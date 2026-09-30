

# File tp\_power.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_power.c**](tp__power_8c.md)

[Go to the documentation of this file](tp__power_8c.md)


```C++

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
        // log_debug("Changing LVDS pin to %u", enabled);
        // log_debug("Pin is at %u", wius_gpio_get(lvds_pwr_switch_pin));
        break;
    case TP_POWER_DOMAIN_POS_HV:
        wius_gpio_put(pos_hv_pin, enabled);
        // log_debug("Changing +HV pin to %u", enabled);
        // log_debug("Pin is at %u", wius_gpio_get(pos_hv_pin));
        break;
    case TP_POWER_DOMAIN_NEG_HV:
        wius_gpio_put(neg_hv_pin, enabled);
        // log_debug("Changing -HV pin to %u", enabled);
        // log_debug("Pin is at %u", wius_gpio_get(neg_hv_pin));
        break;
    case TP_POWER_DOMAIN_NEG_5V:
        wius_gpio_put(neg_5v_pin, enabled);
        // log_debug("Changing -5V pin to %u", enabled);
        // log_debug("Pin is at %u", wius_gpio_get(neg_5v_pin));
        break;
    case TP_POWER_DOMAIN_PLL_PWD:
        // TODO
        // log_debug("Changing PLL pin to %u", enabled);
        //    log_debug("Pin is at %u", wius_gpio_ulp_pin_get(lvds_pwr_switch_pin));
        log_warn("Not implemented");
        break;
    default:
        return;
    }
}
```


