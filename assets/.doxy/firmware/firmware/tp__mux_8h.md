

# File tp\_mux.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_mux.h**](tp__mux_8h.md)

[Go to the source code of this file](tp__mux_8h_source.md)

_TinyProbe SPI MUX driver header file._ [More...](#detailed-description)

* `#include "common.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**tp\_mux**](#enum-tp_mux)  <br>_Mux selection enumeration._  |
| typedef enum [**tp\_mux**](tp__mux_8h.md#enum-tp_mux) | [**tp\_mux\_t**](#typedef-tp_mux_t)  <br>_Mux selection enumeration._  |




















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




    
## Public Types Documentation




### enum tp\_mux 

_Mux selection enumeration._ 
```C++
enum tp_mux {
    TP_MUX_PLL = 0b00,
    TP_MUX_FPGA = 0b01,
    TP_MUX_AFE = 0b10,
    TP_MUX_TX = 0b11
};
```




<hr>



### typedef tp\_mux\_t 

_Mux selection enumeration._ 
```C++
typedef enum tp_mux  tp_mux_t;
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
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_mux.h`

