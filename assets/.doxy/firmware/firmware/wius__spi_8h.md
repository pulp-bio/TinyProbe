

# File wius\_spi.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_spi.h**](wius__spi_8h.md)

[Go to the source code of this file](wius__spi_8h_source.md)

_WiUS SPI implementation header file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "sl_si91x_gspi.h"`
* `#include "sl_si91x_ssi.h"`
* `#include "wius_gpio.h"`















## Classes

| Type | Name |
| ---: | :--- |
| struct | [**wius\_spi\_config**](structwius__spi__config.md) <br>_SPI instance configuration._  |
| struct | [**wius\_spi\_inst**](structwius__spi__inst.md) <br>_SPI instance enumeration._  |


## Public Types

| Type | Name |
| ---: | :--- |
| typedef struct [**wius\_spi\_config**](structwius__spi__config.md) | [**wius\_spi\_config\_t**](#typedef-wius_spi_config_t)  <br>_SPI instance configuration._  |
| enum  | [**wius\_spi\_cs\_mode**](#enum-wius_spi_cs_mode)  <br>_SPI chip select modes enumeration._  |
| typedef enum [**wius\_spi\_cs\_mode**](wius__spi_8h.md#enum-wius_spi_cs_mode) | [**wius\_spi\_cs\_mode\_t**](#typedef-wius_spi_cs_mode_t)  <br>_SPI chip select modes enumeration._  |
| union  | [**instance**](#union-instance)  <br> |
| typedef struct [**wius\_spi\_inst**](structwius__spi__inst.md) | [**wius\_spi\_inst\_t**](#typedef-wius_spi_inst_t)  <br>_SPI instance enumeration._  |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_spi\_await**](#function-wius_spi_await) (uint8\_t id) <br>_Await SPI transfer completion._  |
|  [**wius\_spi\_inst\_t**](wius__spi_8h.md#typedef-wius_spi_inst_t) | [**wius\_spi\_get\_instance**](#function-wius_spi_get_instance) (uint8\_t id) <br>_Get SPI instance by ID._  |
|  sl\_status\_t | [**wius\_spi\_init**](#function-wius_spi_init) (uint8\_t id, [**wius\_spi\_config\_t**](wius__spi_8h.md#typedef-wius_spi_config_t) \* config) <br>_Initialize SPI module._  |
|  sl\_status\_t | [**wius\_spi\_send**](#function-wius_spi_send) (uint8\_t id, const uint8\_t \* tx\_buf, size\_t len, bool wait) <br>_Send data over SPI without receiving data._  |
|  sl\_status\_t | [**wius\_spi\_xfer**](#function-wius_spi_xfer) (uint8\_t id, uint8\_t \* tx\_buf, uint8\_t \* rx\_buf, size\_t len, bool wait) <br>_Transfer data over SPI._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**WIUS\_SPI\_INST\_0**](wius__spi_8h.md#define-wius_spi_inst_0)  `0`<br> |
| define  | [**WIUS\_SPI\_INST\_1**](wius__spi_8h.md#define-wius_spi_inst_1)  `1`<br> |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### typedef wius\_spi\_config\_t 

_SPI instance configuration._ 
```C++
typedef struct wius_spi_config  wius_spi_config_t;
```




<hr>



### enum wius\_spi\_cs\_mode 

_SPI chip select modes enumeration._ 
```C++
enum wius_spi_cs_mode {
    WIUS_SPI_CS_NONE = SL_GSPI_MASTER_UNUSED,
    WIUS_SPI_CS_SW = SL_GSPI_MASTER_SW,
    WIUS_SPI_CS_HW = SL_GSPI_MASTER_HW_OUTPUT
};
```




<hr>



### typedef wius\_spi\_cs\_mode\_t 

_SPI chip select modes enumeration._ 
```C++
typedef enum wius_spi_cs_mode  wius_spi_cs_mode_t;
```




<hr>



### union instance 

```C++

```



&lt; Peripheral handle union 

    

<hr>



### typedef wius\_spi\_inst\_t 

_SPI instance enumeration._ 
```C++
typedef struct wius_spi_inst  wius_spi_inst_t;
```




<hr>
## Public Functions Documentation




### function wius\_spi\_await 

_Await SPI transfer completion._ 
```C++
sl_status_t wius_spi_await (
    uint8_t id
) 
```





**Parameters:**


* `id` SPI instance to await



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_TIMEOUT` Timeout occured (See [**WIUS\_SPI\_RX\_TIMEOUT**](config_8h.md#define-wius_spi_rx_timeout)) 
* `SL_STATUS_FAIL` Error during acquiring semaphores 



        

<hr>



### function wius\_spi\_get\_instance 

_Get SPI instance by ID._ 
```C++
wius_spi_inst_t wius_spi_get_instance (
    uint8_t id
) 
```





**Parameters:**


* `id` SPI instance ID



**Returns:**

Pointer to the SPI instance structure 




        

<hr>



### function wius\_spi\_init 

_Initialize SPI module._ 
```C++
sl_status_t wius_spi_init (
    uint8_t id,
    wius_spi_config_t * config
) 
```





**Parameters:**


* `id` SPI instance to initialize 
* `config` Pointer to the SPI configuration



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_INVALID_PARAMETER` Invalid instance 
* `other` Error during peripheral initialization 



        

<hr>



### function wius\_spi\_send 

_Send data over SPI without receiving data._ 
```C++
sl_status_t wius_spi_send (
    uint8_t id,
    const uint8_t * tx_buf,
    size_t len,
    bool wait
) 
```





**Parameters:**


* `id` SPI instance to use for transfer 
* `tx_buf` Pointer to the buffer containing the data to be sent 
* `len` Number of bytes to send 
* `wait` Wait for transfer to complete



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during transfer or waiting 



        

<hr>



### function wius\_spi\_xfer 

_Transfer data over SPI._ 
```C++
sl_status_t wius_spi_xfer (
    uint8_t id,
    uint8_t * tx_buf,
    uint8_t * rx_buf,
    size_t len,
    bool wait
) 
```





**Parameters:**


* `id` SPI instance to use for transfer 
* `tx_buf` Pointer to the buffer containing the data to be sent 
* `rx_buf` Pointer to the buffer where the received data will be stored 
* `len` Number of bytes to transfer 
* `wait` Wait for transfer to complete



**Return value:**


* `SL_STATUS_OK` Success 
* `other` Error during transfer or waiting 



        

<hr>
## Macro Definition Documentation





### define WIUS\_SPI\_INST\_0 

```C++
#define WIUS_SPI_INST_0 `0`
```



Instance 0 on pins [25, 26, 27, 53] (GSPI Master) 

        

<hr>



### define WIUS\_SPI\_INST\_1 

```C++
#define WIUS_SPI_INST_1 `1`
```



Instance 1 on pins [8, 9, 10, 11] (SSI Master) 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_spi.h`

