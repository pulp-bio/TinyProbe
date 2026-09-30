

# File tp\_afe.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_afe.h**](tp__afe_8h.md)

[Go to the source code of this file](tp__afe_8h_source.md)

_TinyProbe AFE driver header file._ [More...](#detailed-description)

* `#include "common.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**tp\_afe\_patt**](#enum-tp_afe_patt)  <br>_AFE test pattern enumeration._  |
| typedef enum [**tp\_afe\_patt**](tp__afe_8h.md#enum-tp_afe_patt) | [**tp\_afe\_patt\_t**](#typedef-tp_afe_patt_t)  <br>_AFE test pattern enumeration._  |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**tp\_afe\_init**](#function-tp_afe_init) (void) <br>_AFE initialization._  |
|  sl\_status\_t | [**tp\_afe\_read\_reg**](#function-tp_afe_read_reg) (uint8\_t address, uint16\_t \* value) <br>_Read from a register of the AFE._  |
|  sl\_status\_t | [**tp\_afe\_read\_reg\_dtgc**](#function-tp_afe_read_reg_dtgc) (uint8\_t address, uint16\_t \* value) <br>_Read from a register of the AFE in the DTGC (Digital Time Gain Compensation) block._  |
|  sl\_status\_t | [**tp\_afe\_test\_pattern**](#function-tp_afe_test_pattern) ([**tp\_afe\_patt\_t**](tp__afe_8h.md#typedef-tp_afe_patt_t) pattern) <br>_AFE test pattern selection._  |
|  sl\_status\_t | [**tp\_afe\_write\_reg**](#function-tp_afe_write_reg) (uint8\_t address, uint16\_t value) <br>_Write to a register of the AFE._  |
|  sl\_status\_t | [**tp\_afe\_write\_reg\_dtgc**](#function-tp_afe_write_reg_dtgc) (uint8\_t address, uint16\_t value) <br>_Write to a register of the AFE in the DTGC (Digital Time Gain Compensation) block._  |
|  sl\_status\_t | [**tp\_afe\_write\_reg\_dtgc\_safe**](#function-tp_afe_write_reg_dtgc_safe) (uint8\_t address, uint16\_t value) <br>_Write to a register of the AFE in the DTGC (Digital Time Gain Compensation) block and check if the write was successful._  |
|  sl\_status\_t | [**tp\_afe\_write\_reg\_safe**](#function-tp_afe_write_reg_safe) (uint8\_t address, uint16\_t value) <br>_Write to a register of the AFE and check if the write was successful._  |




























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




### enum tp\_afe\_patt 

_AFE test pattern enumeration._ 
```C++
enum tp_afe_patt {
    NORMAL_OPERATION = 0,
    HALF_ZEROS_HALF_ONES,
    ALTERN_ZERO_ONE,
    CUSTOM,
    ALL_ONES,
    TOGGLE,
    ALL_ZEROS,
    RAMP
};
```




<hr>



### typedef tp\_afe\_patt\_t 

_AFE test pattern enumeration._ 
```C++
typedef enum tp_afe_patt  tp_afe_patt_t;
```




<hr>
## Public Functions Documentation




### function tp\_afe\_init 

_AFE initialization._ 
```C++
sl_status_t tp_afe_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers



**Note:**

This function must be called before any other AFE function 




        

<hr>



### function tp\_afe\_read\_reg 

_Read from a register of the AFE._ 
```C++
sl_status_t tp_afe_read_reg (
    uint8_t address,
    uint16_t * value
) 
```





**Parameters:**


* `address` Address of the register to read from 
* `value` Pointer to the variable where the value of the register will be stored



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during SPI transfer 



        

<hr>



### function tp\_afe\_read\_reg\_dtgc 

_Read from a register of the AFE in the DTGC (Digital Time Gain Compensation) block._ 
```C++
sl_status_t tp_afe_read_reg_dtgc (
    uint8_t address,
    uint16_t * value
) 
```





**Parameters:**


* `address` Address of the register to read from 
* `value` Pointer to the variable where the value of the register will be stored



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during SPI transfer 



        

<hr>



### function tp\_afe\_test\_pattern 

_AFE test pattern selection._ 
```C++
sl_status_t tp_afe_test_pattern (
    tp_afe_patt_t pattern
) 
```





**Parameters:**


* `pattern` Test pattern to be applied



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers 



        

<hr>



### function tp\_afe\_write\_reg 

_Write to a register of the AFE._ 
```C++
sl_status_t tp_afe_write_reg (
    uint8_t address,
    uint16_t value
) 
```





**Parameters:**


* `address` Address of the register to write to 
* `value` Value to write to the register



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during SPI transfer 



        

<hr>



### function tp\_afe\_write\_reg\_dtgc 

_Write to a register of the AFE in the DTGC (Digital Time Gain Compensation) block._ 
```C++
sl_status_t tp_afe_write_reg_dtgc (
    uint8_t address,
    uint16_t value
) 
```





**Parameters:**


* `address` Address of the register to write to 
* `value` Value to write to the register



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during SPI transfer 



        

<hr>



### function tp\_afe\_write\_reg\_dtgc\_safe 

_Write to a register of the AFE in the DTGC (Digital Time Gain Compensation) block and check if the write was successful._ 
```C++
sl_status_t tp_afe_write_reg_dtgc_safe (
    uint8_t address,
    uint16_t value
) 
```





**Parameters:**


* `address` Address of the register to write to 
* `value` Value to write to the register



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Write was not successful 
* `other` Error during SPI transfer 



        

<hr>



### function tp\_afe\_write\_reg\_safe 

_Write to a register of the AFE and check if the write was successful._ 
```C++
sl_status_t tp_afe_write_reg_safe (
    uint8_t address,
    uint16_t value
) 
```





**Parameters:**


* `address` Address of the register to write to 
* `value` Value to write to the register



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Write was not successful 
* `other` Error during SPI transfer 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_afe.h`

