

# File tp\_power.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_power.c**](tp__power_8c.md)

[Go to the source code of this file](tp__power_8c_source.md)

_TinyProbe power management driver source file._ [More...](#detailed-description)

* `#include "tp_power.h"`
* `#include "wius_gpio.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**lvds\_pwr\_switch\_pin**](#variable-lvds_pwr_switch_pin)   = `[**WIUS\_GPIO\_ULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_ulp_output)([**TP\_POWER\_GPIO\_LVDS\_PWR\_SW**](config_8h.md#define-tp_power_gpio_lvds_pwr_sw))`<br> |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**neg\_5v\_pin**](#variable-neg_5v_pin)   = `[**WIUS\_GPIO\_ULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_ulp_output)([**TP\_POWER\_GPIO\_NEG\_5V**](config_8h.md#define-tp_power_gpio_neg_5v))`<br> |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**neg\_hv\_pin**](#variable-neg_hv_pin)   = `[**WIUS\_GPIO\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_output)([**TP\_POWER\_GPIO\_NEG\_HV**](config_8h.md#define-tp_power_gpio_neg_hv))`<br> |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**pos\_hv\_pin**](#variable-pos_hv_pin)   = `[**WIUS\_GPIO\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_output)([**TP\_POWER\_GPIO\_POS\_HV**](config_8h.md#define-tp_power_gpio_pos_hv))`<br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**tp\_power\_init**](#function-tp_power_init) (void) <br>_Initialize the power control module._  |
|  void | [**tp\_power\_on**](#function-tp_power_on) (void) <br>_Initialize the power domain of the TinyProbe._  |
|  void | [**tp\_power\_set**](#function-tp_power_set) ([**tp\_power\_domain\_t**](tp__power_8h.md#typedef-tp_power_domain_t) domain, bool enabled) <br>_Enable or disable a power domain._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich 




**Author:**

Sergei Vostrikov, ETH Zürich




    
## Public Attributes Documentation




### variable lvds\_pwr\_switch\_pin 

```C++
wius_gpio_t lvds_pwr_switch_pin;
```




<hr>



### variable neg\_5v\_pin 

```C++
wius_gpio_t neg_5v_pin;
```




<hr>



### variable neg\_hv\_pin 

```C++
wius_gpio_t neg_hv_pin;
```




<hr>



### variable pos\_hv\_pin 

```C++
wius_gpio_t pos_hv_pin;
```




<hr>
## Public Functions Documentation




### function tp\_power\_init 

_Initialize the power control module._ 
```C++
void tp_power_init (
    void
) 
```




<hr>



### function tp\_power\_on 

_Initialize the power domain of the TinyProbe._ 
```C++
void tp_power_on (
    void
) 
```




<hr>



### function tp\_power\_set 

_Enable or disable a power domain._ 
```C++
void tp_power_set (
    tp_power_domain_t domain,
    bool enabled
) 
```





**Parameters:**


* `domain` Power domain to enable or disable 
* `enabled` True to enable, false to disable 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_power.c`

