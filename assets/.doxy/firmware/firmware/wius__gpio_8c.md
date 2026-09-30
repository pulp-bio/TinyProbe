

# File wius\_gpio.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_gpio.c**](wius__gpio_8c.md)

[Go to the source code of this file](wius__gpio_8c_source.md)

_WiUS GPIO implementation source file._ [More...](#detailed-description)

* `#include "wius_gpio.h"`























## Public Static Attributes

| Type | Name |
| ---: | :--- |
|  uint32\_t | [**\_wius\_gpio\_active\_interrupts**](#variable-_wius_gpio_active_interrupts)   = `0`<br> |
|  uint32\_t | [**\_wius\_gpio\_ulp\_active\_interrupts**](#variable-_wius_gpio_ulp_active_interrupts)   = `0`<br> |
|  uint32\_t | [**\_wius\_gpio\_uulp\_active\_interrupts**](#variable-_wius_gpio_uulp_active_interrupts)   = `0`<br> |














## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_gpio\_attach\_interrupt**](#function-wius_gpio_attach_interrupt) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio, [**wius\_gpio\_interrupt\_t**](wius__gpio_8h.md#typedef-wius_gpio_interrupt_t) trigger, [**wius\_gpio\_callback\_t**](wius__gpio_8h.md#typedef-wius_gpio_callback_t) function) <br>_Attach interrupt to GPIO pin._  |
|  sl\_status\_t | [**wius\_gpio\_config**](#function-wius_gpio_config) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio) <br>_Configure GPIO pin._  |
|  uint8\_t | [**wius\_gpio\_get**](#function-wius_gpio_get) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio) <br>_Get GPIO pin state._  |
|  sl\_status\_t | [**wius\_gpio\_init**](#function-wius_gpio_init) (void) <br>_Initialize GPIO module._  |
|  void | [**wius\_gpio\_put**](#function-wius_gpio_put) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio, bool on) <br>_Set GPIO pin state._  |
|  void | [**wius\_gpio\_toggle**](#function-wius_gpio_toggle) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio) <br>_Toggle GPIO pin state._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Static Attributes Documentation




### variable \_wius\_gpio\_active\_interrupts 

```C++
uint32_t _wius_gpio_active_interrupts;
```




<hr>



### variable \_wius\_gpio\_ulp\_active\_interrupts 

```C++
uint32_t _wius_gpio_ulp_active_interrupts;
```




<hr>



### variable \_wius\_gpio\_uulp\_active\_interrupts 

```C++
uint32_t _wius_gpio_uulp_active_interrupts;
```




<hr>
## Public Functions Documentation




### function wius\_gpio\_attach\_interrupt 

_Attach interrupt to GPIO pin._ 
```C++
sl_status_t wius_gpio_attach_interrupt (
    wius_gpio_t gpio,
    wius_gpio_interrupt_t trigger,
    wius_gpio_callback_t function
) 
```





**Parameters:**


* `gpio` GPIO pin definition 
* `trigger` Interrupt trigger (see [**wius\_gpio\_interrupt\_t**](wius__gpio_8h.md#typedef-wius_gpio_interrupt_t)) 
* `function` Interrupt callback function



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_INVALID_STATE` Pin is not an input or maximum number of interrupts reached 



        

<hr>



### function wius\_gpio\_config 

_Configure GPIO pin._ 
```C++
sl_status_t wius_gpio_config (
    wius_gpio_t gpio
) 
```





**Parameters:**


* `gpio` GPIO pin definition



**Return value:**


* `SL_STATUS_OK` Success 
* `other` GPIO configuration failed



**Note:**

Must be called before using the pin 




**Note:**

Must be called after [**wius\_gpio\_init**](wius__gpio_8h.md#function-wius_gpio_init) 




        

<hr>



### function wius\_gpio\_get 

_Get GPIO pin state._ 
```C++
uint8_t wius_gpio_get (
    wius_gpio_t gpio
) 
```





**Parameters:**


* `gpio` GPIO pin definition



**Returns:**

GPIO pin state (0 = low, 1 = high) 




        

<hr>



### function wius\_gpio\_init 

_Initialize GPIO module._ 
```C++
sl_status_t wius_gpio_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` GPIO initialization failed 



        

<hr>



### function wius\_gpio\_put 

_Set GPIO pin state._ 
```C++
void wius_gpio_put (
    wius_gpio_t gpio,
    bool on
) 
```





**Parameters:**


* `gpio` GPIO pin definition 
* `on` State to set (true = high, false = low) 



        

<hr>



### function wius\_gpio\_toggle 

_Toggle GPIO pin state._ 
```C++
void wius_gpio_toggle (
    wius_gpio_t gpio
) 
```





**Parameters:**


* `gpio` GPIO pin definition 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_gpio.c`

