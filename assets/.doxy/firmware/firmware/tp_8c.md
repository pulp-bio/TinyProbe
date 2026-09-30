

# File tp.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**tp.c**](tp_8c.md)

[Go to the source code of this file](tp_8c_source.md)

_TinyProbe main source file._ [More...](#detailed-description)

* `#include "tp.h"`
* `#include <stdint.h>`
* `#include "sl_si91x_power_manager.h"`
* `#include "tp_methods.h"`
* `#include "tp_mux.h"`
* `#include "tp_fpga.h"`
* `#include "tp_afe.h"`
* `#include "tp_tx.h"`
* `#include "tp_power.h"`
* `#include "wius_power.h"`
* `#include "wius_wifi.h"`
* `#include "wius_spi.h"`
* `#include "wius_tcp.h"`
* `#include "wius_gpio.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**int\_pin**](#variable-int_pin)   = `[**WIUS\_GPIO\_UULP\_INPUT**](wius__gpio_8h.md#define-wius_gpio_uulp_input)([**TP\_GPIO\_INT**](config_8h.md#define-tp_gpio_int))`<br> |
|  [**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) | [**msg**](#variable-msg)  <br> |
|  [**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) | [**payload**](#variable-payload)   = `{0}`<br> |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**reset\_pin**](#variable-reset_pin)   = `[**WIUS\_GPIO\_ULP\_OUTPUT**](wius__gpio_8h.md#define-wius_gpio_ulp_output)([**TP\_GPIO\_RESET**](config_8h.md#define-tp_gpio_reset))`<br> |
|  char | [**rsp\_buffer**](#variable-rsp_buffer)  <br> |
|  size\_t | [**rsp\_buffer\_len**](#variable-rsp_buffer_len)   = `0`<br> |
|  osSemaphoreId\_t | [**sem\_fpga**](#variable-sem_fpga)  <br> |
|  [**wius\_spi\_config\_t**](wius__spi_8h.md#typedef-wius_spi_config_t) | [**spi\_config**](#variable-spi_config)   = `/* multi line expression */`<br> |
|  [**wius\_spi\_inst\_t**](wius__spi_8h.md#typedef-wius_spi_inst_t) | [**spi\_inst**](#variable-spi_inst)  <br> |
|  [**tp\_buffer\_t**](structtp__buffer__t.md) | [**tp\_buf**](#variable-tp_buf)  <br> |
|  [**wius\_wifi\_mdns\_t**](wius__wifi_8h.md#typedef-wius_wifi_mdns_t) | [**tp\_mdns**](#variable-tp_mdns)   = `/* multi line expression */`<br> |
|  uint8\_t | [**wifi\_rx\_buffer**](#variable-wifi_rx_buffer)   = `{0}`<br> |
|  osThreadId\_t | [**wifi\_transmit\_thread\_id**](#variable-wifi_transmit_thread_id)  <br> |
|  osThreadAttr\_t | [**wifi\_tx\_thread\_attr**](#variable-wifi_tx_thread_attr)   = `/* multi line expression */`<br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**\_tp\_int\_handler**](#function-_tp_int_handler) (uint32\_t flag) <br> |
|  void | [**\_tp\_thread\_wifi\_transmit**](#function-_tp_thread_wifi_transmit) (void \* argument) <br> |
|  sl\_status\_t | [**tp\_init**](#function-tp_init) (void) <br>_Initialize the FPGA (SPI, GPIOs, register values)_  |
|  sl\_status\_t | [**tp\_main\_thread**](#function-tp_main_thread) (void) <br>_TinyProbe main thread._  |
|  void | [**vApplicationStackOverflowHook**](#function-vapplicationstackoverflowhook) (void \* xTask, char \* pcTaskName) <br> |


## Public Static Functions

| Type | Name |
| ---: | :--- |
|  void | [**\_tp\_nanopb\_sender**](#function-_tp_nanopb_sender) (const char \* response, size\_t response\_len) <br> |


























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




### variable int\_pin 

```C++
wius_gpio_t int_pin;
```




<hr>



### variable msg 

```C++
wius_tcp_server_message_t msg;
```




<hr>



### variable payload 

```C++
wius_tcp_server_message_t payload;
```




<hr>



### variable reset\_pin 

```C++
wius_gpio_t reset_pin;
```




<hr>



### variable rsp\_buffer 

```C++
char rsp_buffer[1024];
```




<hr>



### variable rsp\_buffer\_len 

```C++
size_t rsp_buffer_len;
```




<hr>



### variable sem\_fpga 

```C++
osSemaphoreId_t sem_fpga;
```



Semaphore raised by FPGA interrupts 

        

<hr>



### variable spi\_config 

```C++
wius_spi_config_t spi_config;
```




<hr>



### variable spi\_inst 

```C++
wius_spi_inst_t spi_inst;
```




<hr>



### variable tp\_buf 

```C++
tp_buffer_t tp_buf;
```



Buffer for storing acquired data 

        

<hr>



### variable tp\_mdns 

```C++
wius_wifi_mdns_t tp_mdns;
```




<hr>



### variable wifi\_rx\_buffer 

```C++
uint8_t wifi_rx_buffer[TP_WIFI_RX_BUFFER_SIZE];
```




<hr>



### variable wifi\_transmit\_thread\_id 

```C++
osThreadId_t wifi_transmit_thread_id;
```




<hr>



### variable wifi\_tx\_thread\_attr 

```C++
osThreadAttr_t wifi_tx_thread_attr;
```




<hr>
## Public Functions Documentation




### function \_tp\_int\_handler 

```C++
void _tp_int_handler (
    uint32_t flag
) 
```




<hr>



### function \_tp\_thread\_wifi\_transmit 

```C++
void _tp_thread_wifi_transmit (
    void * argument
) 
```




<hr>



### function tp\_init 

_Initialize the FPGA (SPI, GPIOs, register values)_ 
```C++
sl_status_t tp_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` SPI, GPIO interrupt or register initialization failed 



        

<hr>



### function tp\_main\_thread 

_TinyProbe main thread._ 
```C++
sl_status_t tp_main_thread (
    void
) 
```




<hr>



### function vApplicationStackOverflowHook 

```C++
void vApplicationStackOverflowHook (
    void * xTask,
    char * pcTaskName
) 
```




<hr>
## Public Static Functions Documentation




### function \_tp\_nanopb\_sender 

```C++
static void _tp_nanopb_sender (
    const char * response,
    size_t response_len
) 
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/tp.c`

