

# File wius\_spi.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_spi.c**](wius__spi_8c.md)

[Go to the source code of this file](wius__spi_8c_source.md)

_WiUS SPI implementation source file._ [More...](#detailed-description)

* `#include "wius_spi.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**wius\_spi\_wait\_mode\_t**](#enum-wius_spi_wait_mode_t)  <br> |




## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**wius\_spi\_inst\_t**](wius__spi_8h.md#typedef-wius_spi_inst_t) | [**\_wius\_spi\_0\_instance**](#variable-_wius_spi_0_instance)   = `{0}`<br> |
|  osSemaphoreId\_t | [**\_wius\_spi\_0\_sem**](#variable-_wius_spi_0_sem)  <br> |
|  [**wius\_spi\_inst\_t**](wius__spi_8h.md#typedef-wius_spi_inst_t) | [**\_wius\_spi\_1\_instance**](#variable-_wius_spi_1_instance)   = `{0}`<br> |
|  osSemaphoreId\_t | [**\_wius\_spi\_1\_sem**](#variable-_wius_spi_1_sem)  <br> |


## Public Static Attributes

| Type | Name |
| ---: | :--- |
|  bool | [**\_wius\_spi\_0\_complete**](#variable-_wius_spi_0_complete)   = `false`<br> |
|  uint32\_t | [**\_wius\_spi\_0\_event**](#variable-_wius_spi_0_event)   = `0`<br> |
|  wius\_spi\_wait\_mode\_t | [**\_wius\_spi\_0\_wait\_mode**](#variable-_wius_spi_0_wait_mode)   = `WIUS\_SPI\_WAIT\_IDLE`<br> |














## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**\_wius\_spi\_cs\_active**](#function-_wius_spi_cs_active) (uint8\_t id) <br> |
|  void | [**\_wius\_spi\_cs\_inactive**](#function-_wius_spi_cs_inactive) (uint8\_t id) <br> |
|  sl\_status\_t | [**wius\_spi\_await**](#function-wius_spi_await) (uint8\_t id) <br>_Await SPI transfer completion._  |
|  [**wius\_spi\_inst\_t**](wius__spi_8h.md#typedef-wius_spi_inst_t) | [**wius\_spi\_get\_instance**](#function-wius_spi_get_instance) (uint8\_t id) <br>_Get SPI instance by ID._  |
|  sl\_status\_t | [**wius\_spi\_init**](#function-wius_spi_init) (uint8\_t id, [**wius\_spi\_config\_t**](wius__spi_8h.md#typedef-wius_spi_config_t) \* config) <br>_Initialize SPI module._  |
|  sl\_status\_t | [**wius\_spi\_send**](#function-wius_spi_send) (uint8\_t id, const uint8\_t \* tx\_buf, size\_t len, bool wait) <br>_Send data over SPI without receiving data._  |
|  sl\_status\_t | [**wius\_spi\_xfer**](#function-wius_spi_xfer) (uint8\_t id, uint8\_t \* tx\_buf, uint8\_t \* rx\_buf, size\_t len, bool wait) <br>_Transfer data over SPI._  |


## Public Static Functions

| Type | Name |
| ---: | :--- |
|  void | [**\_wius\_spi\_gspi\_callback**](#function-_wius_spi_gspi_callback) (uint32\_t event) <br> |
|  sl\_status\_t | [**\_wius\_spi\_gspi\_event\_status**](#function-_wius_spi_gspi_event_status) (uint32\_t event) <br> |
|  sl\_status\_t | [**\_wius\_spi\_poll\_gspi**](#function-_wius_spi_poll_gspi) (void) <br> |
|  void | [**\_wius\_spi\_prepare\_gspi\_wait**](#function-_wius_spi_prepare_gspi_wait) (bool poll) <br> |
|  void | [**\_wius\_spi\_ssi\_callback**](#function-_wius_spi_ssi_callback) (uint32\_t event) <br> |


























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### enum wius\_spi\_wait\_mode\_t 

```C++
enum wius_spi_wait_mode_t {
    WIUS_SPI_WAIT_IDLE,
    WIUS_SPI_WAIT_POLL,
    WIUS_SPI_WAIT_SEMAPHORE
};
```




<hr>
## Public Attributes Documentation




### variable \_wius\_spi\_0\_instance 

```C++
wius_spi_inst_t _wius_spi_0_instance;
```




<hr>



### variable \_wius\_spi\_0\_sem 

```C++
osSemaphoreId_t _wius_spi_0_sem;
```




<hr>



### variable \_wius\_spi\_1\_instance 

```C++
wius_spi_inst_t _wius_spi_1_instance;
```




<hr>



### variable \_wius\_spi\_1\_sem 

```C++
osSemaphoreId_t _wius_spi_1_sem;
```




<hr>
## Public Static Attributes Documentation




### variable \_wius\_spi\_0\_complete 

```C++
volatile bool _wius_spi_0_complete;
```




<hr>



### variable \_wius\_spi\_0\_event 

```C++
volatile uint32_t _wius_spi_0_event;
```




<hr>



### variable \_wius\_spi\_0\_wait\_mode 

```C++
volatile wius_spi_wait_mode_t _wius_spi_0_wait_mode;
```




<hr>
## Public Functions Documentation




### function \_wius\_spi\_cs\_active 

```C++
void _wius_spi_cs_active (
    uint8_t id
) 
```




<hr>



### function \_wius\_spi\_cs\_inactive 

```C++
void _wius_spi_cs_inactive (
    uint8_t id
) 
```




<hr>



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
## Public Static Functions Documentation




### function \_wius\_spi\_gspi\_callback 

```C++
static void _wius_spi_gspi_callback (
    uint32_t event
) 
```




<hr>



### function \_wius\_spi\_gspi\_event\_status 

```C++
static sl_status_t _wius_spi_gspi_event_status (
    uint32_t event
) 
```




<hr>



### function \_wius\_spi\_poll\_gspi 

```C++
static sl_status_t _wius_spi_poll_gspi (
    void
) 
```




<hr>



### function \_wius\_spi\_prepare\_gspi\_wait 

```C++
static void _wius_spi_prepare_gspi_wait (
    bool poll
) 
```




<hr>



### function \_wius\_spi\_ssi\_callback 

```C++
static void _wius_spi_ssi_callback (
    uint32_t event
) 
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_spi.c`

