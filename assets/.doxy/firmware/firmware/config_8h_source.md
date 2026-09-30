

# File config.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**config.h**](config_8h.md)

[Go to the documentation of this file](config_8h.md)


```C++

#pragma once

#include "env.h"

#define WIUS_BOARD 3

#define LOG_MAX_CALLBACKS 1
#define LOG_BUFFER_SIZE 128
#define LOG_ONCE
#define LOG_NO_COLOR

#define WIUS_SPI_FREQ 32000000
#define WIUS_SPI_RX_TIMEOUT 100
#define WIUS_SPI_SHORT_XFER_MAX 16
#define WIUS_SPI_EXT_CS0 53
#define WIUS_SPI_EXT_CS1 0

#ifndef WIUS_WIFI_SSID
#error "Please define WIUS_WIFI_SSID in env.h"
#endif
#ifndef WIUS_WIFI_PASS
#error "Please define WIUS_WIFI_PASS in env.h"
#endif
#define WIUS_WIFI_DEVICE_NAME "WiUS"

#define TP_TEST_MODE 0
#define TP_PROBE_ID 1
#define TP_WIFI_RX_BUFFER_SIZE 1472
#define TP_UDP_PACKET_SIZE 1000
#define TP_UDP_PACKET_AMT 1
#define TP_UDP_PORT 50007
#define TP_TCP_PORT 50008
#define TP_GPIO_INT 2
#define TP_GPIO_RESET 10
#define TP_THREAD_STACK_MAIN 4500
#define TP_THREAD_STACK_WIFI 1500

#define TP_AFE_SPI_DELAY_NS 0

#define TP_BUFFER_NUM 10
#define TP_FIFO_READ_SIZE (TP_UDP_PACKET_SIZE * TP_UDP_PACKET_AMT)
#define TP_BUFFER_SIZE (TP_FIFO_READ_SIZE + 2)

#define TP_RESPONSE_BUFFER_SIZE 1024
#define TP_METHOD_TIMING 0

#define TP_FPGA_SPI_DELAY_NS 50

#define TP_MUX_GPIO_EXTINT 3
#define TP_MUX_GPIO_AFETX 1

#define TP_POWER_GPIO_NEG_5V 2
#define TP_POWER_GPIO_NEG_HV 52
#define TP_POWER_GPIO_POS_HV 56
#define TP_POWER_GPIO_LVDS_PWR_SW 8

// Don't touch this, here we transfer some configurations to all the drivers
#define RSI_DHCP_HOST_NAME WIUS_WIFI_DEVICE_NAME 
```


