

# File wius\_power.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_power.h**](wius__power_8h.md)

[Go to the source code of this file](wius__power_8h_source.md)

_WiUS power management header file._ [More...](#detailed-description)

* `#include "common.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**wius\_power\_mode**](#enum-wius_power_mode)  <br>_WiUS power modes enumeration._  |
| typedef enum [**wius\_power\_mode**](wius__power_8h.md#enum-wius_power_mode) | [**wius\_power\_mode\_t**](#typedef-wius_power_mode_t)  <br>_WiUS power modes enumeration._  |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_power\_init**](#function-wius_power_init) (void) <br>_Initialize the power management module._  |
|  sl\_status\_t | [**wius\_power\_set**](#function-wius_power_set) ([**wius\_power\_mode\_t**](wius__power_8h.md#typedef-wius_power_mode_t) mode) <br>_Set the power mode._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### enum wius\_power\_mode 

_WiUS power modes enumeration._ 
```C++
enum wius_power_mode {
    WIUS_POWER_MODE_LOW = 0,
    WIUS_POWER_MODE_HIGH
};
```




<hr>



### typedef wius\_power\_mode\_t 

_WiUS power modes enumeration._ 
```C++
typedef enum wius_power_mode  wius_power_mode_t;
```




<hr>
## Public Functions Documentation




### function wius\_power\_init 

_Initialize the power management module._ 
```C++
sl_status_t wius_power_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Power management initialization failed 



        

<hr>



### function wius\_power\_set 

_Set the power mode._ 
```C++
sl_status_t wius_power_set (
    wius_power_mode_t mode
) 
```





**Parameters:**


* `mode` Power mode to set ([**wius\_power\_mode\_t**](wius__power_8h.md#typedef-wius_power_mode_t)) 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_power.h`

