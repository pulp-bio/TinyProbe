

# File tp\_fpga.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_fpga.c**](tp__fpga_8c.md)

[Go to the source code of this file](tp__fpga_8c_source.md)

_TinyProbe FPGA driver source file._ [More...](#detailed-description)

* `#include "tp_fpga.h"`
* `#include "wius_spi.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  uint8\_t | [**default\_registers**](#variable-default_registers)   = `/* multi line expression */`<br> |
|  uint32\_t | [**default\_values**](#variable-default_values)   = `/* multi line expression */`<br> |
















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



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**MEM\_CTRL\_RD\_CMD**](tp__fpga_8c.md#define-mem_ctrl_rd_cmd)  `0`<br> |
| define  | [**MEM\_CTRL\_WR\_CMD**](tp__fpga_8c.md#define-mem_ctrl_wr_cmd)  `1`<br> |
| define  | [**SPI\_DUMMY\_ADDR**](tp__fpga_8c.md#define-spi_dummy_addr)  `0`<br> |
| define  | [**SPI\_READ\_CFG**](tp__fpga_8c.md#define-spi_read_cfg)  `1`<br> |
| define  | [**SPI\_WRITE\_CFG**](tp__fpga_8c.md#define-spi_write_cfg)  `2`<br> |
| define  | [**SPI\_WR\_FIFO**](tp__fpga_8c.md#define-spi_wr_fifo)  `17`<br> |
| define  | [**SP\_RD\_FIFO**](tp__fpga_8c.md#define-sp_rd_fifo)  `16`<br> |
| define  | [**SYS\_CTRL\_CMD\_DUMMY**](tp__fpga_8c.md#define-sys_ctrl_cmd_dummy)  `0`<br> |
| define  | [**SYS\_CTRL\_CMD\_ECHO**](tp__fpga_8c.md#define-sys_ctrl_cmd_echo)  `4`<br> |
| define  | [**SYS\_CTRL\_CMD\_RD\_EN**](tp__fpga_8c.md#define-sys_ctrl_cmd_rd_en)  `3`<br> |
| define  | [**SYS\_CTRL\_CMD\_RESET**](tp__fpga_8c.md#define-sys_ctrl_cmd_reset)  `2`<br> |
| define  | [**SYS\_CTRL\_CMD\_START**](tp__fpga_8c.md#define-sys_ctrl_cmd_start)  `1`<br> |
| define  | [**TP\_NUM\_DEFAULT\_REGS**](tp__fpga_8c.md#define-tp_num_default_regs)  `10`<br> |

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




### variable default\_registers 

```C++
uint8_t default_registers[TP_NUM_DEFAULT_REGS];
```




<hr>



### variable default\_values 

```C++
uint32_t default_values[TP_NUM_DEFAULT_REGS];
```




<hr>
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
## Macro Definition Documentation





### define MEM\_CTRL\_RD\_CMD 

```C++
#define MEM_CTRL_RD_CMD `0`
```




<hr>



### define MEM\_CTRL\_WR\_CMD 

```C++
#define MEM_CTRL_WR_CMD `1`
```




<hr>



### define SPI\_DUMMY\_ADDR 

```C++
#define SPI_DUMMY_ADDR `0`
```




<hr>



### define SPI\_READ\_CFG 

```C++
#define SPI_READ_CFG `1`
```




<hr>



### define SPI\_WRITE\_CFG 

```C++
#define SPI_WRITE_CFG `2`
```




<hr>



### define SPI\_WR\_FIFO 

```C++
#define SPI_WR_FIFO `17`
```




<hr>



### define SP\_RD\_FIFO 

```C++
#define SP_RD_FIFO `16`
```




<hr>



### define SYS\_CTRL\_CMD\_DUMMY 

```C++
#define SYS_CTRL_CMD_DUMMY `0`
```




<hr>



### define SYS\_CTRL\_CMD\_ECHO 

```C++
#define SYS_CTRL_CMD_ECHO `4`
```




<hr>



### define SYS\_CTRL\_CMD\_RD\_EN 

```C++
#define SYS_CTRL_CMD_RD_EN `3`
```




<hr>



### define SYS\_CTRL\_CMD\_RESET 

```C++
#define SYS_CTRL_CMD_RESET `2`
```




<hr>



### define SYS\_CTRL\_CMD\_START 

```C++
#define SYS_CTRL_CMD_START `1`
```




<hr>



### define TP\_NUM\_DEFAULT\_REGS 

```C++
#define TP_NUM_DEFAULT_REGS `10`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/hal/tp_fpga.c`

