

# File wius\_gpio.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_gpio.h**](wius__gpio_8h.md)

[Go to the source code of this file](wius__gpio_8h_source.md)

_WiUS GPIO implementation header file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "sl_gpio_board.h"`
* `#include "sl_si91x_driver_gpio.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| typedef sl\_gpio\_irq\_callback\_t | [**wius\_gpio\_callback\_t**](#typedef-wius_gpio_callback_t)  <br>_GPIO callback function type._  |
| enum  | [**wius\_gpio\_interrupt**](#enum-wius_gpio_interrupt)  <br>_GPIO interrupt trigger enumeration._  |
| typedef enum [**wius\_gpio\_interrupt**](wius__gpio_8h.md#enum-wius_gpio_interrupt) | [**wius\_gpio\_interrupt\_t**](#typedef-wius_gpio_interrupt_t)  <br>_GPIO interrupt trigger enumeration._  |
| typedef sl\_si91x\_gpio\_pin\_config\_t | [**wius\_gpio\_t**](#typedef-wius_gpio_t)  <br>_GPIO pin definition._  |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_gpio\_attach\_interrupt**](#function-wius_gpio_attach_interrupt) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio, [**wius\_gpio\_interrupt\_t**](wius__gpio_8h.md#typedef-wius_gpio_interrupt_t) trigger, [**wius\_gpio\_callback\_t**](wius__gpio_8h.md#typedef-wius_gpio_callback_t) function) <br>_Attach interrupt to GPIO pin._  |
|  sl\_status\_t | [**wius\_gpio\_config**](#function-wius_gpio_config) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio) <br>_Configure GPIO pin._  |
|  uint8\_t | [**wius\_gpio\_get**](#function-wius_gpio_get) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio) <br>_Get GPIO pin state._  |
|  sl\_status\_t | [**wius\_gpio\_init**](#function-wius_gpio_init) (void) <br>_Initialize GPIO module._  |
|  void | [**wius\_gpio\_put**](#function-wius_gpio_put) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio, bool on) <br>_Set GPIO pin state._  |
|  void | [**wius\_gpio\_toggle**](#function-wius_gpio_toggle) ([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) gpio) <br>_Toggle GPIO pin state._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**WIUS\_GPIO\_INPUT**](wius__gpio_8h.md#define-wius_gpio_input) (NUM) `([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t)) { {\_WIUS\_GPIO\_PORT(NUM), \_WIUS\_GPIO\_PIN(NUM)}, GPIO\_INPUT }`<br>_GPIO input pin definition._  |
| define  | [**WIUS\_GPIO\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_output) (NUM) `([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t)) { {\_WIUS\_GPIO\_PORT(NUM), \_WIUS\_GPIO\_PIN(NUM)}, GPIO\_OUTPUT }`<br>_GPIO output pin definition._  |
| define  | [**WIUS\_GPIO\_ULP\_INPUT**](wius__gpio_8h.md#define-wius_gpio_ulp_input) (NUM) `([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t)) { {\_WIUS\_GPIO\_ULP\_PORT(NUM), \_WIUS\_GPIO\_ULP\_PIN(NUM)}, GPIO\_INPUT }`<br>_ULP GPIO input pin definition._  |
| define  | [**WIUS\_GPIO\_ULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_ulp_output) (NUM) `([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t)) { {\_WIUS\_GPIO\_ULP\_PORT(NUM), \_WIUS\_GPIO\_ULP\_PIN(NUM)}, GPIO\_OUTPUT }`<br>_ULP GPIO output pin definition._  |
| define  | [**WIUS\_GPIO\_UULP\_INPUT**](wius__gpio_8h.md#define-wius_gpio_uulp_input) (NUM) `([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t)) { {\_WIUS\_GPIO\_UULP\_PORT(NUM), \_WIUS\_GPIO\_UULP\_PIN(NUM)}, GPIO\_INPUT }`<br>_UULP GPIO input pin definition._  |
| define  | [**WIUS\_GPIO\_UULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_uulp_output) (NUM) `([**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t)) { {\_WIUS\_GPIO\_UULP\_PORT(NUM), \_WIUS\_GPIO\_UULP\_PIN(NUM)}, GPIO\_OUTPUT }`<br>_UULP GPIO output pin definition._  |
| define  | [**\_WIUS\_GPIO\_PIN**](wius__gpio_8h.md#define-_wius_gpio_pin) (num) `num`<br> |
| define  | [**\_WIUS\_GPIO\_PORT**](wius__gpio_8h.md#define-_wius_gpio_port) (num) `SL\_GPIO\_PORT\_A`<br> |
| define  | [**\_WIUS\_GPIO\_ULP\_PIN**](wius__gpio_8h.md#define-_wius_gpio_ulp_pin) (num) `num`<br> |
| define  | [**\_WIUS\_GPIO\_ULP\_PORT**](wius__gpio_8h.md#define-_wius_gpio_ulp_port) (num) `SL\_GPIO\_ULP\_PORT`<br> |
| define  | [**\_WIUS\_GPIO\_UULP\_PIN**](wius__gpio_8h.md#define-_wius_gpio_uulp_pin) (num) `num`<br> |
| define  | [**\_WIUS\_GPIO\_UULP\_PORT**](wius__gpio_8h.md#define-_wius_gpio_uulp_port) (num) `SL\_GPIO\_UULP\_PORT`<br> |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### typedef wius\_gpio\_callback\_t 

_GPIO callback function type._ 
```C++
typedef sl_gpio_irq_callback_t wius_gpio_callback_t;
```




<hr>



### enum wius\_gpio\_interrupt 

_GPIO interrupt trigger enumeration._ 
```C++
enum wius_gpio_interrupt {
    WIUS_GPIO_INT_HIGH = SL_GPIO_INTERRUPT_HIGH,
    WIUS_GPIO_INT_LOW = SL_GPIO_INTERRUPT_LOW,
    WIUS_GPIO_INT_RISING = SL_GPIO_INTERRUPT_RISING_EDGE,
    WIUS_GPIO_INT_FALLING = SL_GPIO_INTERRUPT_FALLING_EDGE,
    WIUS_GPIO_INT_TOGGLE = SL_GPIO_INTERRUPT_RISE_FALL_EDGE
};
```




<hr>



### typedef wius\_gpio\_interrupt\_t 

_GPIO interrupt trigger enumeration._ 
```C++
typedef enum wius_gpio_interrupt  wius_gpio_interrupt_t;
```




<hr>



### typedef wius\_gpio\_t 

_GPIO pin definition._ 
```C++
typedef sl_si91x_gpio_pin_config_t wius_gpio_t;
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
## Macro Definition Documentation





### define WIUS\_GPIO\_INPUT 

_GPIO input pin definition._ 
```C++
#define WIUS_GPIO_INPUT (
    NUM
) `( wius_gpio_t ) { {_WIUS_GPIO_PORT(NUM), _WIUS_GPIO_PIN(NUM)}, GPIO_INPUT }`
```





**Parameters:**


* `NUM` GPIO pin number 



        

<hr>



### define WIUS\_GPIO\_OUTPUT 

_GPIO output pin definition._ 
```C++
#define WIUS_GPIO_OUTPUT (
    NUM
) `( wius_gpio_t ) { {_WIUS_GPIO_PORT(NUM), _WIUS_GPIO_PIN(NUM)}, GPIO_OUTPUT }`
```





**Parameters:**


* `NUM` GPIO pin number 



        

<hr>



### define WIUS\_GPIO\_ULP\_INPUT 

_ULP GPIO input pin definition._ 
```C++
#define WIUS_GPIO_ULP_INPUT (
    NUM
) `( wius_gpio_t ) { {_WIUS_GPIO_ULP_PORT(NUM), _WIUS_GPIO_ULP_PIN(NUM)}, GPIO_INPUT }`
```





**Parameters:**


* `NUM` GPIO pin number 



        

<hr>



### define WIUS\_GPIO\_ULP\_OUTPUT 

_ULP GPIO output pin definition._ 
```C++
#define WIUS_GPIO_ULP_OUTPUT (
    NUM
) `( wius_gpio_t ) { {_WIUS_GPIO_ULP_PORT(NUM), _WIUS_GPIO_ULP_PIN(NUM)}, GPIO_OUTPUT }`
```





**Parameters:**


* `NUM` GPIO pin number 



        

<hr>



### define WIUS\_GPIO\_UULP\_INPUT 

_UULP GPIO input pin definition._ 
```C++
#define WIUS_GPIO_UULP_INPUT (
    NUM
) `( wius_gpio_t ) { {_WIUS_GPIO_UULP_PORT(NUM), _WIUS_GPIO_UULP_PIN(NUM)}, GPIO_INPUT }`
```





**Parameters:**


* `NUM` GPIO pin number 



        

<hr>



### define WIUS\_GPIO\_UULP\_OUTPUT 

_UULP GPIO output pin definition._ 
```C++
#define WIUS_GPIO_UULP_OUTPUT (
    NUM
) `( wius_gpio_t ) { {_WIUS_GPIO_UULP_PORT(NUM), _WIUS_GPIO_UULP_PIN(NUM)}, GPIO_OUTPUT }`
```





**Parameters:**


* `NUM` GPIO pin number 



        

<hr>



### define \_WIUS\_GPIO\_PIN 

```C++
#define _WIUS_GPIO_PIN (
    num
) `num`
```




<hr>



### define \_WIUS\_GPIO\_PORT 

```C++
#define _WIUS_GPIO_PORT (
    num
) `SL_GPIO_PORT_A`
```




<hr>



### define \_WIUS\_GPIO\_ULP\_PIN 

```C++
#define _WIUS_GPIO_ULP_PIN (
    num
) `num`
```




<hr>



### define \_WIUS\_GPIO\_ULP\_PORT 

```C++
#define _WIUS_GPIO_ULP_PORT (
    num
) `SL_GPIO_ULP_PORT`
```




<hr>



### define \_WIUS\_GPIO\_UULP\_PIN 

```C++
#define _WIUS_GPIO_UULP_PIN (
    num
) `num`
```




<hr>



### define \_WIUS\_GPIO\_UULP\_PORT 

```C++
#define _WIUS_GPIO_UULP_PORT (
    num
) `SL_GPIO_UULP_PORT`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_gpio.h`

