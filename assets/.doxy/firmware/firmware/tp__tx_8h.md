

# File tp\_tx.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_tx.h**](tp__tx_8h.md)

[Go to the source code of this file](tp__tx_8h_source.md)

_TinyProbe TX chip driver header file._ [More...](#detailed-description)

* `#include "common.h"`





































## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**tp\_tx\_init**](#function-tp_tx_init) (void) <br>_TX initialization._  |
|  sl\_status\_t | [**tp\_tx\_read\_reg**](#function-tp_tx_read_reg) (uint16\_t address, uint32\_t \* value) <br>_Read from a register of the TX._  |
|  sl\_status\_t | [**tp\_tx\_write\_reg**](#function-tp_tx_write_reg) (uint16\_t address, uint32\_t value) <br>_Write to a register of the TX._  |
|  sl\_status\_t | [**tp\_tx\_write\_reg\_safe**](#function-tp_tx_write_reg_safe) (uint16\_t address, uint32\_t value) <br>_Write to a register of the TX and check if the write was successful._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich 




**Author:**

Sergei Vostrikov, ETH Zürich




    
## Public Functions Documentation




### function tp\_tx\_init 

_TX initialization._ 
```C++
sl_status_t tp_tx_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers



**Note:**

This function must be called before any other TX function 




        

<hr>



### function tp\_tx\_read\_reg 

_Read from a register of the TX._ 
```C++
sl_status_t tp_tx_read_reg (
    uint16_t address,
    uint32_t * value
) 
```





**Parameters:**


* `address` Address of the register to read from 
* `value` Pointer to the value read from the register



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during reading from registers 



        

<hr>



### function tp\_tx\_write\_reg 

_Write to a register of the TX._ 
```C++
sl_status_t tp_tx_write_reg (
    uint16_t address,
    uint32_t value
) 
```





**Parameters:**


* `address` Address of the register to write to 
* `value` Value to write to the register



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers 



        

<hr>



### function tp\_tx\_write\_reg\_safe 

_Write to a register of the TX and check if the write was successful._ 
```C++
sl_status_t tp_tx_write_reg_safe (
    uint16_t address,
    uint32_t value
) 
```





**Parameters:**


* `address` Address of the register to write to 
* `value` Value to write to the register



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Write was not successful 
* `other` Error during writing to registers 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_tx.h`

