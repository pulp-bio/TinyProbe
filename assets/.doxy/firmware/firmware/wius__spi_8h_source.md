

# File wius\_spi.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_spi.h**](wius__spi_8h.md)

[Go to the documentation of this file](wius__spi_8h.md)


```C++

#pragma once

#include "common.h"

#include "sl_si91x_gspi.h"
#include "sl_si91x_ssi.h"

#include "wius_gpio.h"

#define WIUS_SPI_INST_0 0 
#define WIUS_SPI_INST_1 1 
typedef enum wius_spi_cs_mode
{
    WIUS_SPI_CS_NONE = SL_GSPI_MASTER_UNUSED, 
    WIUS_SPI_CS_SW = SL_GSPI_MASTER_SW,       
    WIUS_SPI_CS_HW = SL_GSPI_MASTER_HW_OUTPUT 
} wius_spi_cs_mode_t;

typedef struct wius_spi_config
{
    uint8_t width;              
    uint8_t mode;               
    uint32_t freq;              
    wius_spi_cs_mode_t cs_mode; 
    uint8_t cs_pin;             
    uint8_t cs_polarity;        
} wius_spi_config_t;

typedef struct wius_spi_inst
{
    uint8_t id;               
    wius_spi_config_t config; 
    wius_gpio_t cs;           
    union instance 
    {
        sl_gspi_handle_t gspi; 
        sl_ssi_handle_t ssi;   
    } inst;                    
} wius_spi_inst_t;

wius_spi_inst_t wius_spi_get_instance(uint8_t id);

sl_status_t wius_spi_init(uint8_t id, wius_spi_config_t *config);

sl_status_t wius_spi_xfer(uint8_t id, uint8_t *tx_buf, uint8_t *rx_buf, size_t len, bool wait);

sl_status_t wius_spi_send(uint8_t id, const uint8_t *tx_buf, size_t len, bool wait);

sl_status_t wius_spi_await(uint8_t id);
```


