

# File tp\_afe.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_afe.c**](tp__afe_8c.md)

[Go to the source code of this file](tp__afe_8c_source.md)

_TinyProbe AFE driver source file._ [More...](#detailed-description)

* `#include "tp_afe.h"`
* `#include "wius_spi.h"`















## Classes

| Type | Name |
| ---: | :--- |
| struct | [**\_tp\_afe\_reg**](struct__tp__afe__reg.md) <br> |


## Public Types

| Type | Name |
| ---: | :--- |
| typedef struct [**\_tp\_afe\_reg**](struct__tp__afe__reg.md) | [**\_tp\_afe\_reg\_t**](#typedef-_tp_afe_reg_t)  <br> |




## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**\_tp\_afe\_reg\_t**](struct__tp__afe__reg.md) const | [**tp\_afe\_adc\_vca\_reg\_init\_seq**](#variable-tp_afe_adc_vca_reg_init_seq)  <br> |
|  [**\_tp\_afe\_reg\_t**](struct__tp__afe__reg.md) const | [**tp\_afe\_dtgc\_reg\_init\_seq**](#variable-tp_afe_dtgc_reg_init_seq)  <br> |
















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



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**ADC\_REG\_41\_PLLRST1**](tp__afe_8c.md#define-adc_reg_41_pllrst1)  `0x4000`<br> |
| define  | [**ADC\_REG\_42\_PLLRST2**](tp__afe_8c.md#define-adc_reg_42_pllrst2)  `0x4000`<br> |
| define  | [**AFE\_SOFT\_RST**](tp__afe_8c.md#define-afe_soft_rst)  `0x01`<br> |
| define  | [**DTGC\_WR\_EN**](tp__afe_8c.md#define-dtgc_wr_en)  `0x10`<br> |
| define  | [**NUM\_OF\_ADC\_VCA\_REGS**](tp__afe_8c.md#define-num_of_adc_vca_regs)  `(55 + 23)`<br> |
| define  | [**NUM\_OF\_DTGC\_REGS**](tp__afe_8c.md#define-num_of_dtgc_regs)  `(23)`<br> |
| define  | [**REG\_READ\_EN**](tp__afe_8c.md#define-reg_read_en)  `0x02`<br> |

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




### typedef \_tp\_afe\_reg\_t 

```C++
typedef struct _tp_afe_reg  _tp_afe_reg_t;
```




<hr>
## Public Attributes Documentation




### variable tp\_afe\_adc\_vca\_reg\_init\_seq 

```C++
_tp_afe_reg_t const tp_afe_adc_vca_reg_init_seq[NUM_OF_ADC_VCA_REGS];
```




<hr>



### variable tp\_afe\_dtgc\_reg\_init\_seq 

```C++
_tp_afe_reg_t const tp_afe_dtgc_reg_init_seq[NUM_OF_DTGC_REGS];
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
## Macro Definition Documentation





### define ADC\_REG\_41\_PLLRST1 

```C++
#define ADC_REG_41_PLLRST1 `0x4000`
```




<hr>



### define ADC\_REG\_42\_PLLRST2 

```C++
#define ADC_REG_42_PLLRST2 `0x4000`
```




<hr>



### define AFE\_SOFT\_RST 

```C++
#define AFE_SOFT_RST `0x01`
```




<hr>



### define DTGC\_WR\_EN 

```C++
#define DTGC_WR_EN `0x10`
```




<hr>



### define NUM\_OF\_ADC\_VCA\_REGS 

```C++
#define NUM_OF_ADC_VCA_REGS `(55 + 23)`
```




<hr>



### define NUM\_OF\_DTGC\_REGS 

```C++
#define NUM_OF_DTGC_REGS `(23)`
```




<hr>



### define REG\_READ\_EN 

```C++
#define REG_READ_EN `0x02`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_afe.c`

