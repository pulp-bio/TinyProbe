

# File config.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**config.h**](config_8h.md)

[Go to the source code of this file](config_8h_source.md)

_Configuration header file._ [More...](#detailed-description)

* `#include "env.h"`
































































## Macros

| Type | Name |
| ---: | :--- |
| define  | [**LOG\_BUFFER\_SIZE**](config_8h.md#define-log_buffer_size)  `128`<br>_Remove lifetime of log library (no deinitialization, no callback unregistration)_  |
| define  | [**LOG\_MAX\_CALLBACKS**](config_8h.md#define-log_max_callbacks)  `1`<br>_&lt; Maximum number of log callbacks that can be registered_  |
| define  | [**LOG\_NO\_COLOR**](config_8h.md#define-log_no_color)  <br> |
| define  | [**LOG\_ONCE**](config_8h.md#define-log_once)  <br> |
| define  | [**RSI\_DHCP\_HOST\_NAME**](config_8h.md#define-rsi_dhcp_host_name)  `[**WIUS\_WIFI\_DEVICE\_NAME**](config_8h.md#define-wius_wifi_device_name)`<br> |
| define  | [**TP\_AFE\_SPI\_DELAY\_NS**](config_8h.md#define-tp_afe_spi_delay_ns)  `0`<br>_Delay after SPI transfers in ns._  |
| define  | [**TP\_BUFFER\_NUM**](config_8h.md#define-tp_buffer_num)  `10`<br>_Number of buffers available for data acquisition._  |
| define  | [**TP\_BUFFER\_SIZE**](config_8h.md#define-tp_buffer_size)  `([**TP\_FIFO\_READ\_SIZE**](config_8h.md#define-tp_fifo_read_size) + 2)`<br>_Size of one buffer in bytes (FIFO read size + 2 bytes for packet index)_  |
| define  | [**TP\_FIFO\_READ\_SIZE**](config_8h.md#define-tp_fifo_read_size)  `([**TP\_UDP\_PACKET\_SIZE**](config_8h.md#define-tp_udp_packet_size) \* [**TP\_UDP\_PACKET\_AMT**](config_8h.md#define-tp_udp_packet_amt))`<br>_FIFO read size in bytes._  |
| define  | [**TP\_FPGA\_SPI\_DELAY\_NS**](config_8h.md#define-tp_fpga_spi_delay_ns)  `50`<br>_Delay after SPI transfers in ns._  |
| define  | [**TP\_GPIO\_INT**](config_8h.md#define-tp_gpio_int)  `2`<br>_FPGA Interrupt UULP gpio number._  |
| define  | [**TP\_GPIO\_RESET**](config_8h.md#define-tp_gpio_reset)  `10`<br>_FPGA Reset ULP gpio number._  |
| define  | [**TP\_METHOD\_TIMING**](config_8h.md#define-tp_method_timing)  `0`<br>_Enable per-method DWT timing logs._  |
| define  | [**TP\_MUX\_GPIO\_AFETX**](config_8h.md#define-tp_mux_gpio_afetx)  `1`<br>_AFE TX MUX ULP gpio number._  |
| define  | [**TP\_MUX\_GPIO\_EXTINT**](config_8h.md#define-tp_mux_gpio_extint)  `3`<br>_EXT INT MUX UULP gpio number._  |
| define  | [**TP\_POWER\_GPIO\_LVDS\_PWR\_SW**](config_8h.md#define-tp_power_gpio_lvds_pwr_sw)  `8`<br>_LVDS power switch ULP gpio number._  |
| define  | [**TP\_POWER\_GPIO\_NEG\_5V**](config_8h.md#define-tp_power_gpio_neg_5v)  `2`<br>_-5V ULP gpio number_  |
| define  | [**TP\_POWER\_GPIO\_NEG\_HV**](config_8h.md#define-tp_power_gpio_neg_hv)  `52`<br>_-HV gpio number_  |
| define  | [**TP\_POWER\_GPIO\_POS\_HV**](config_8h.md#define-tp_power_gpio_pos_hv)  `56`<br>_+HV gpio number_  |
| define  | [**TP\_PROBE\_ID**](config_8h.md#define-tp_probe_id)  `1`<br>_ID of the probe (used for Ping responses)_  |
| define  | [**TP\_RESPONSE\_BUFFER\_SIZE**](config_8h.md#define-tp_response_buffer_size)  `1024`<br>_Response buffer size for JSON-RPC methods in bytes._  |
| define  | [**TP\_TCP\_PORT**](config_8h.md#define-tp_tcp_port)  `50008`<br>_Port on which TCP transfers happen._  |
| define  | [**TP\_TEST\_MODE**](config_8h.md#define-tp_test_mode)  `0`<br>_Enable test mode (1=enabled, 0=disabled). Used for testing acquisition code without actual TinyProbe hardware._  |
| define  | [**TP\_THREAD\_STACK\_MAIN**](config_8h.md#define-tp_thread_stack_main)  `4500`<br>_Stack size for main thread._  |
| define  | [**TP\_THREAD\_STACK\_WIFI**](config_8h.md#define-tp_thread_stack_wifi)  `1500`<br>_Stack size for WiFi thread._  |
| define  | [**TP\_UDP\_PACKET\_AMT**](config_8h.md#define-tp_udp_packet_amt)  `1`<br>_Number of packets to acquire per SPI before sending._  |
| define  | [**TP\_UDP\_PACKET\_SIZE**](config_8h.md#define-tp_udp_packet_size)  `1000`<br>_Size of one UDP packet (no header)_  |
| define  | [**TP\_UDP\_PORT**](config_8h.md#define-tp_udp_port)  `50007`<br>_Port on which UDP transfers happen._  |
| define  | [**TP\_WIFI\_RX\_BUFFER\_SIZE**](config_8h.md#define-tp_wifi_rx_buffer_size)  `1472`<br>_Size of the WiFi RX buffer._  |
| define  | [**WIUS\_BOARD**](config_8h.md#define-wius_board)  `3`<br>_&lt; Board type for WiUS firmware. Can be one of 0: "DK2605A", 1: "EK2708A", 2: "PK6031A", 3: "WIUS1"._  |
| define  | [**WIUS\_SPI\_EXT\_CS0**](config_8h.md#define-wius_spi_ext_cs0)  `53`<br>_CS pin number for instance 0 (set to 0 if unused)_  |
| define  | [**WIUS\_SPI\_EXT\_CS1**](config_8h.md#define-wius_spi_ext_cs1)  `0`<br>_CS pin number for instance 1 (set to 0 if unused)_  |
| define  | [**WIUS\_SPI\_FREQ**](config_8h.md#define-wius_spi_freq)  `32000000`<br>_SPI clock frequency in Hz._  |
| define  | [**WIUS\_SPI\_RX\_TIMEOUT**](config_8h.md#define-wius_spi_rx_timeout)  `100`<br>_SPI timeout for transmission in ticks._  |
| define  | [**WIUS\_SPI\_SHORT\_XFER\_MAX**](config_8h.md#define-wius_spi_short_xfer_max)  `16`<br>_Maximum transfer size that waits by polling an interrupt-updated flag._  |
| define  | [**WIUS\_WIFI\_DEVICE\_NAME**](config_8h.md#define-wius_wifi_device_name)  `"WiUS"`<br>_Device name for WiFi._  |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Macro Definition Documentation





### define LOG\_BUFFER\_SIZE 

_Remove lifetime of log library (no deinitialization, no callback unregistration)_ 
```C++
#define LOG_BUFFER_SIZE `128`
```




<hr>



### define LOG\_MAX\_CALLBACKS 

_&lt; Maximum number of log callbacks that can be registered_ 
```C++
#define LOG_MAX_CALLBACKS `1`
```



Size of the log buffer in bytes 

        

<hr>



### define LOG\_NO\_COLOR 

```C++
#define LOG_NO_COLOR 
```




<hr>



### define LOG\_ONCE 

```C++
#define LOG_ONCE 
```




<hr>



### define RSI\_DHCP\_HOST\_NAME 

```C++
#define RSI_DHCP_HOST_NAME `WIUS_WIFI_DEVICE_NAME`
```



Host name for DHCP 

        

<hr>



### define TP\_AFE\_SPI\_DELAY\_NS 

_Delay after SPI transfers in ns._ 
```C++
#define TP_AFE_SPI_DELAY_NS `0`
```




<hr>



### define TP\_BUFFER\_NUM 

_Number of buffers available for data acquisition._ 
```C++
#define TP_BUFFER_NUM `10`
```




<hr>



### define TP\_BUFFER\_SIZE 

_Size of one buffer in bytes (FIFO read size + 2 bytes for packet index)_ 
```C++
#define TP_BUFFER_SIZE `( TP_FIFO_READ_SIZE + 2)`
```




<hr>



### define TP\_FIFO\_READ\_SIZE 

_FIFO read size in bytes._ 
```C++
#define TP_FIFO_READ_SIZE `( TP_UDP_PACKET_SIZE * TP_UDP_PACKET_AMT )`
```




<hr>



### define TP\_FPGA\_SPI\_DELAY\_NS 

_Delay after SPI transfers in ns._ 
```C++
#define TP_FPGA_SPI_DELAY_NS `50`
```




<hr>



### define TP\_GPIO\_INT 

_FPGA Interrupt UULP gpio number._ 
```C++
#define TP_GPIO_INT `2`
```




<hr>



### define TP\_GPIO\_RESET 

_FPGA Reset ULP gpio number._ 
```C++
#define TP_GPIO_RESET `10`
```




<hr>



### define TP\_METHOD\_TIMING 

_Enable per-method DWT timing logs._ 
```C++
#define TP_METHOD_TIMING `0`
```




<hr>



### define TP\_MUX\_GPIO\_AFETX 

_AFE TX MUX ULP gpio number._ 
```C++
#define TP_MUX_GPIO_AFETX `1`
```




<hr>



### define TP\_MUX\_GPIO\_EXTINT 

_EXT INT MUX UULP gpio number._ 
```C++
#define TP_MUX_GPIO_EXTINT `3`
```




<hr>



### define TP\_POWER\_GPIO\_LVDS\_PWR\_SW 

_LVDS power switch ULP gpio number._ 
```C++
#define TP_POWER_GPIO_LVDS_PWR_SW `8`
```




<hr>



### define TP\_POWER\_GPIO\_NEG\_5V 

_-5V ULP gpio number_ 
```C++
#define TP_POWER_GPIO_NEG_5V `2`
```




<hr>



### define TP\_POWER\_GPIO\_NEG\_HV 

_-HV gpio number_ 
```C++
#define TP_POWER_GPIO_NEG_HV `52`
```




<hr>



### define TP\_POWER\_GPIO\_POS\_HV 

_+HV gpio number_ 
```C++
#define TP_POWER_GPIO_POS_HV `56`
```




<hr>



### define TP\_PROBE\_ID 

_ID of the probe (used for Ping responses)_ 
```C++
#define TP_PROBE_ID `1`
```




<hr>



### define TP\_RESPONSE\_BUFFER\_SIZE 

_Response buffer size for JSON-RPC methods in bytes._ 
```C++
#define TP_RESPONSE_BUFFER_SIZE `1024`
```




<hr>



### define TP\_TCP\_PORT 

_Port on which TCP transfers happen._ 
```C++
#define TP_TCP_PORT `50008`
```




<hr>



### define TP\_TEST\_MODE 

_Enable test mode (1=enabled, 0=disabled). Used for testing acquisition code without actual TinyProbe hardware._ 
```C++
#define TP_TEST_MODE `0`
```




<hr>



### define TP\_THREAD\_STACK\_MAIN 

_Stack size for main thread._ 
```C++
#define TP_THREAD_STACK_MAIN `4500`
```




<hr>



### define TP\_THREAD\_STACK\_WIFI 

_Stack size for WiFi thread._ 
```C++
#define TP_THREAD_STACK_WIFI `1500`
```




<hr>



### define TP\_UDP\_PACKET\_AMT 

_Number of packets to acquire per SPI before sending._ 
```C++
#define TP_UDP_PACKET_AMT `1`
```




<hr>



### define TP\_UDP\_PACKET\_SIZE 

_Size of one UDP packet (no header)_ 
```C++
#define TP_UDP_PACKET_SIZE `1000`
```




<hr>



### define TP\_UDP\_PORT 

_Port on which UDP transfers happen._ 
```C++
#define TP_UDP_PORT `50007`
```




<hr>



### define TP\_WIFI\_RX\_BUFFER\_SIZE 

_Size of the WiFi RX buffer._ 
```C++
#define TP_WIFI_RX_BUFFER_SIZE `1472`
```




<hr>



### define WIUS\_BOARD 

_&lt; Board type for WiUS firmware. Can be one of 0: "DK2605A", 1: "EK2708A", 2: "PK6031A", 3: "WIUS1"._ 
```C++
#define WIUS_BOARD `3`
```




<hr>



### define WIUS\_SPI\_EXT\_CS0 

_CS pin number for instance 0 (set to 0 if unused)_ 
```C++
#define WIUS_SPI_EXT_CS0 `53`
```




<hr>



### define WIUS\_SPI\_EXT\_CS1 

_CS pin number for instance 1 (set to 0 if unused)_ 
```C++
#define WIUS_SPI_EXT_CS1 `0`
```




<hr>



### define WIUS\_SPI\_FREQ 

_SPI clock frequency in Hz._ 
```C++
#define WIUS_SPI_FREQ `32000000`
```




<hr>



### define WIUS\_SPI\_RX\_TIMEOUT 

_SPI timeout for transmission in ticks._ 
```C++
#define WIUS_SPI_RX_TIMEOUT `100`
```




<hr>



### define WIUS\_SPI\_SHORT\_XFER\_MAX 

_Maximum transfer size that waits by polling an interrupt-updated flag._ 
```C++
#define WIUS_SPI_SHORT_XFER_MAX `16`
```




<hr>



### define WIUS\_WIFI\_DEVICE\_NAME 

_Device name for WiFi._ 
```C++
#define WIUS_WIFI_DEVICE_NAME `"WiUS"`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/config.h`

