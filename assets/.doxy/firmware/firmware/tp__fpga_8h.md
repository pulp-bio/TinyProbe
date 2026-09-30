

# File tp\_fpga.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_fpga.h**](tp__fpga_8h.md)

[Go to the source code of this file](tp__fpga_8h_source.md)

_TinyProbe FPGA driver header file._ [More...](#detailed-description)

* `#include "common.h"`





































## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**tp\_fpga\_empty\_tx**](#function-tp_fpga_empty_tx) (void) <br>_Empty the TX FIFO of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_en\_read**](#function-tp_fpga_en_read) (void) <br>_Enable the readout of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_init**](#function-tp_fpga_init) (void) <br>_FPGA initialization._  |
|  sl\_status\_t | [**tp\_fpga\_read\_cfg**](#function-tp_fpga_read_cfg) (uint8\_t \* value) <br>_Read from the configuration register of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_read\_fifo**](#function-tp_fpga_read_fifo) (uint8\_t \* tx\_buf, uint8\_t \* rx\_buf, uint32\_t len, bool wait) <br>_Read from the FIFO of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_reset\_multififo**](#function-tp_fpga_reset_multififo) (void) <br>_Reset the FIFO of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_send\_cmd**](#function-tp_fpga_send_cmd) (uint8\_t cmd, uint8\_t \* answer) <br>_Send a command to the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_send\_read\_reg\_cmd**](#function-tp_fpga_send_read_reg_cmd) (uint8\_t reg\_addr) <br>_Send a read register command to the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_send\_start**](#function-tp_fpga_send_start) (void) <br>_Send a start command to the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_trigger\_shot**](#function-tp_fpga_trigger_shot) (void) <br>_Trigger a shot on the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_write\_cfg**](#function-tp_fpga_write_cfg) (uint8\_t value) <br>_Write to the configuration register of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_write\_reg**](#function-tp_fpga_write_reg) (uint32\_t reg\_value, uint8\_t reg\_addr) <br>_Write to a register of the FPGA._  |
|  sl\_status\_t | [**tp\_fpga\_write\_reg\_safe**](#function-tp_fpga_write_reg_safe) (uint32\_t reg\_value, uint8\_t reg\_addr) <br>_Write to a register of the FPGA and check if the write was successful._  |




























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




### function tp\_fpga\_empty\_tx 

_Empty the TX FIFO of the FPGA._ 
```C++
sl_status_t tp_fpga_empty_tx (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during emptying the TX FIFO 



        

<hr>



### function tp\_fpga\_en\_read 

_Enable the readout of the FPGA._ 
```C++
sl_status_t tp_fpga_en_read (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during enabling the readout 



        

<hr>



### function tp\_fpga\_init 

_FPGA initialization._ 
```C++
sl_status_t tp_fpga_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers



**Note:**

This function must be called before any other FPGA function 




        

<hr>



### function tp\_fpga\_read\_cfg 

_Read from the configuration register of the FPGA._ 
```C++
sl_status_t tp_fpga_read_cfg (
    uint8_t * value
) 
```





**Parameters:**


* `value` Pointer to the value buffer



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during reading from the register 



        

<hr>



### function tp\_fpga\_read\_fifo 

_Read from the FIFO of the FPGA._ 
```C++
sl_status_t tp_fpga_read_fifo (
    uint8_t * tx_buf,
    uint8_t * rx_buf,
    uint32_t len,
    bool wait
) 
```





**Parameters:**


* `tx_buf` Buffer to write to the FIFO 
* `rx_buf` Buffer to read from the FIFO 
* `len` Length of the buffer 
* `wait` Wait for the transfer to finish



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during reading from the FIFO 



        

<hr>



### function tp\_fpga\_reset\_multififo 

_Reset the FIFO of the FPGA._ 
```C++
sl_status_t tp_fpga_reset_multififo (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during resetting the FIFO 



        

<hr>



### function tp\_fpga\_send\_cmd 

_Send a command to the FPGA._ 
```C++
sl_status_t tp_fpga_send_cmd (
    uint8_t cmd,
    uint8_t * answer
) 
```





**Parameters:**


* `cmd` Command to send 
* `answer` Pointer to the answer buffer



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during sending the command 



        

<hr>



### function tp\_fpga\_send\_read\_reg\_cmd 

_Send a read register command to the FPGA._ 
```C++
sl_status_t tp_fpga_send_read_reg_cmd (
    uint8_t reg_addr
) 
```





**Parameters:**


* `reg_addr` Address of the register to read



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers 



        

<hr>



### function tp\_fpga\_send\_start 

_Send a start command to the FPGA._ 
```C++
sl_status_t tp_fpga_send_start (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during sending the command 



        

<hr>



### function tp\_fpga\_trigger\_shot 

_Trigger a shot on the FPGA._ 
```C++
sl_status_t tp_fpga_trigger_shot (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during triggering the shot 



        

<hr>



### function tp\_fpga\_write\_cfg 

_Write to the configuration register of the FPGA._ 
```C++
sl_status_t tp_fpga_write_cfg (
    uint8_t value
) 
```





**Parameters:**


* `value` Value to write to the configuration register



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers 



        

<hr>



### function tp\_fpga\_write\_reg 

_Write to a register of the FPGA._ 
```C++
sl_status_t tp_fpga_write_reg (
    uint32_t reg_value,
    uint8_t reg_addr
) 
```





**Parameters:**


* `reg_value` Value to write to the register 
* `reg_addr` Address of the register to write to 



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during writing to registers 



        

<hr>



### function tp\_fpga\_write\_reg\_safe 

_Write to a register of the FPGA and check if the write was successful._ 
```C++
sl_status_t tp_fpga_write_reg_safe (
    uint32_t reg_value,
    uint8_t reg_addr
) 
```





**Parameters:**


* `reg_value` Value to write to the register 
* `reg_addr` Address of the register to write to



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Write was not successful 
* `other` Error during writing to registers 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_fpga.h`

