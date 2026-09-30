

# File tp\_mux.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_mux.c**](tp__mux_8c.md)

[Go to the documentation of this file](tp__mux_8c.md)


```C++

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
```


