

# File tp\_power.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_power.h**](tp__power_8h.md)

[Go to the source code of this file](tp__power_8h_source.md)

_TinyProbe power management driver header file._ [More...](#detailed-description)

* `#include "common.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**tp\_power\_domain**](#enum-tp_power_domain)  <br>_Power domain enumeration._  |
| typedef enum [**tp\_power\_domain**](tp__power_8h.md#enum-tp_power_domain) | [**tp\_power\_domain\_t**](#typedef-tp_power_domain_t)  <br>_Power domain enumeration._  |




















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




    
## Public Types Documentation




### enum tp\_power\_domain 

_Power domain enumeration._ 
```C++
enum tp_power_domain {
    TP_POWER_DOMAIN_LVDS_2_5V = 0,
    TP_POWER_DOMAIN_POS_HV,
    TP_POWER_DOMAIN_NEG_HV,
    TP_POWER_DOMAIN_NEG_5V,
    TP_POWER_DOMAIN_PLL_PWD
};
```




<hr>



### typedef tp\_power\_domain\_t 

_Power domain enumeration._ 
```C++
typedef enum tp_power_domain  tp_power_domain_t;
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
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_power.h`

