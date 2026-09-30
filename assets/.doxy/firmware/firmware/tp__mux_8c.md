

# File tp\_mux.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_mux.c**](tp__mux_8c.md)

[Go to the source code of this file](tp__mux_8c_source.md)

_TinyProbe SPI MUX driver source file._ [More...](#detailed-description)

* `#include "tp_mux.h"`
* `#include "wius_gpio.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**afetxmux\_pin**](#variable-afetxmux_pin)   = `[**WIUS\_GPIO\_ULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_ulp_output)([**TP\_MUX\_GPIO\_AFETX**](config_8h.md#define-tp_mux_gpio_afetx))`<br> |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**extintmux\_pin**](#variable-extintmux_pin)   = `[**WIUS\_GPIO\_UULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_uulp_output)([**TP\_MUX\_GPIO\_EXTINT**](config_8h.md#define-tp_mux_gpio_extint))`<br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**tp\_mux\_init**](#function-tp_mux_init) (void) <br>_MUX initialization._  |
|  void | [**tp\_mux\_select**](#function-tp_mux_select) ([**tp\_mux\_t**](tp__mux_8h.md#typedef-tp_mux_t) mux) <br>_MUX select._  |




























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




### variable afetxmux\_pin 

```C++
wius_gpio_t afetxmux_pin;
```




<hr>



### variable extintmux\_pin 

```C++
wius_gpio_t extintmux_pin;
```




<hr>
## Public Functions Documentation




### function tp\_mux\_init 

_MUX initialization._ 
```C++
void tp_mux_init (
    void
) 
```




<hr>



### function tp\_mux\_select 

_MUX select._ 
```C++
void tp_mux_select (
    tp_mux_t mux
) 
```





**Parameters:**


* `mux` Mux to select 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_mux.c`

