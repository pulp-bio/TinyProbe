/**
 * @file wius_spi.c
 *
 * @brief WiUS SPI implementation source file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup wius
 *
 * @parblock
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * @endparblock
 *
 */

#include "wius_spi.h"

osSemaphoreId_t _wius_spi_0_sem;
osSemaphoreId_t _wius_spi_1_sem;

typedef enum
{
    WIUS_SPI_WAIT_IDLE,
    WIUS_SPI_WAIT_POLL,
    WIUS_SPI_WAIT_SEMAPHORE,
} wius_spi_wait_mode_t;

static volatile wius_spi_wait_mode_t _wius_spi_0_wait_mode = WIUS_SPI_WAIT_IDLE;
static volatile uint32_t _wius_spi_0_event = 0;
static volatile bool _wius_spi_0_complete = false;

wius_spi_inst_t _wius_spi_0_instance = {0};
wius_spi_inst_t _wius_spi_1_instance = {0};

static void _wius_spi_gspi_callback(uint32_t event);
static void _wius_spi_ssi_callback(uint32_t event);
static void _wius_spi_prepare_gspi_wait(bool poll);
static sl_status_t _wius_spi_poll_gspi(void);
static sl_status_t _wius_spi_gspi_event_status(uint32_t event);

wius_spi_inst_t wius_spi_get_instance(uint8_t id)
{
    return (id == WIUS_SPI_INST_0) ? _wius_spi_0_instance : _wius_spi_1_instance;
}

sl_status_t wius_spi_init(uint8_t id, wius_spi_config_t *config)
{
    sl_status_t status = SL_STATUS_OK;

    if (id > WIUS_SPI_INST_1)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    wius_spi_inst_t *instance = (id == WIUS_SPI_INST_0) ? &_wius_spi_0_instance : &_wius_spi_1_instance;

    instance->id = id;
    instance->config = *config;
    if (instance->config.cs_mode == WIUS_SPI_CS_SW)
    {
        instance->cs = WIUS_GPIO_OUTPUT(instance->config.cs_pin);
        wius_gpio_config(instance->cs);
        wius_gpio_put(instance->cs, !instance->config.cs_polarity);
    }

    // TODO: Add pin configurations?
    // TODO: Check DMA

    if (instance->id == WIUS_SPI_INST_0) // GSPI
    {
        LOG_RET_STATUS(sl_si91x_gspi_init(SL_GSPI_MASTER, &instance->inst.gspi));

        sl_gspi_control_config_t gspi_config = {
            .bit_width = instance->config.width,
            .bitrate = instance->config.freq,
            .clock_mode = instance->config.mode,
            .slave_select_mode = instance->config.cs_mode,
            .swap_read = false,
            .swap_write = false,
        };
        LOG_RET_STATUS(sl_si91x_gspi_set_configuration(instance->inst.gspi, &gspi_config));
        sl_si91x_gspi_set_slave_number(GSPI_SLAVE_0);

        _wius_spi_0_sem = osSemaphoreNew(1, 0, NULL);
        if (_wius_spi_0_sem == NULL)
        {
            return SL_STATUS_ALLOCATION_FAILED;
        }

        LOG_RET_STATUS(sl_si91x_gspi_register_event_callback(instance->inst.gspi, _wius_spi_gspi_callback));
    }
    else if (instance->id == WIUS_SPI_INST_1) // SSI
    {
        LOG_RET_STATUS(sl_si91x_ssi_init(SL_SSI_MASTER_ACTIVE, &instance->inst.ssi));

        sl_ssi_control_config_t ssi_config = {
            .baud_rate = instance->config.freq,
            .bit_width = instance->config.width,
            .clock_mode = instance->config.mode,
            .device_mode = SL_SSI_MASTER_ACTIVE,
            .receive_sample_delay = 0,
        };
        LOG_RET_STATUS(sl_si91x_ssi_set_configuration(instance->inst.ssi, &ssi_config, SSI_SLAVE_0));
        sl_si91x_ssi_set_slave_number(SSI_SLAVE_0);

        _wius_spi_1_sem = osSemaphoreNew(1, 0, NULL);
        if (_wius_spi_1_sem == NULL)
        {
            return SL_STATUS_ALLOCATION_FAILED;
        }

        LOG_RET_STATUS(sl_si91x_ssi_register_event_callback(instance->inst.ssi, _wius_spi_ssi_callback));
    }
    else
    {
        status = SL_STATUS_INVALID_PARAMETER;
    }

    return status;
}

void _wius_spi_cs_active(uint8_t id)
{
    wius_spi_inst_t *instance = (id == WIUS_SPI_INST_0) ? &_wius_spi_0_instance : &_wius_spi_1_instance;

    if (instance->config.cs_mode == WIUS_SPI_CS_SW)
    {
        wius_gpio_put(instance->cs, instance->config.cs_polarity);
    }
}

void _wius_spi_cs_inactive(uint8_t id)
{
    wius_spi_inst_t *instance = (id == WIUS_SPI_INST_0) ? &_wius_spi_0_instance : &_wius_spi_1_instance;

    if (instance->config.cs_mode == WIUS_SPI_CS_SW)
    {
        wius_gpio_put(instance->cs, !instance->config.cs_polarity);
    }
}

sl_status_t wius_spi_xfer(uint8_t id, uint8_t *tx_buf, uint8_t *rx_buf, size_t len, bool wait)
{
    sl_status_t status = SL_STATUS_OK;

    if (id > WIUS_SPI_INST_1 || tx_buf == NULL || rx_buf == NULL || len == 0)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    wius_spi_inst_t *instance = (id == WIUS_SPI_INST_0) ? &_wius_spi_0_instance : &_wius_spi_1_instance;

    if (instance->id == WIUS_SPI_INST_0) // GSPI
    {
        bool poll = wait && len <= WIUS_SPI_SHORT_XFER_MAX;
        _wius_spi_prepare_gspi_wait(poll);

        _wius_spi_cs_active(instance->id);

        status = sl_si91x_gspi_transfer_data(instance->inst.gspi, tx_buf, rx_buf, len);
        if (status != SL_STATUS_OK)
        {
            _wius_spi_0_wait_mode = WIUS_SPI_WAIT_IDLE;
            _wius_spi_cs_inactive(instance->id);

            return status;
        }

        if (poll)
        {
            return _wius_spi_poll_gspi();
        }
    }
    else if (instance->id == WIUS_SPI_INST_1) // SSI
    {
        _wius_spi_cs_active(instance->id);

        status = sl_si91x_ssi_transfer_data(instance->inst.ssi, tx_buf, rx_buf, len);
        if (status != SL_STATUS_OK)
        {
            _wius_spi_cs_inactive(instance->id);

            return status;
        }
    }
    else
    {
        status = SL_STATUS_INVALID_PARAMETER;
    }

    if (wait)
    {
        LOG_RET_STATUS(wius_spi_await(instance->id));
    }

    return status;
}

sl_status_t wius_spi_send(uint8_t id, const uint8_t *tx_buf, size_t len, bool wait)
{
    sl_status_t status = SL_STATUS_OK;

    if (id > WIUS_SPI_INST_1 || tx_buf == NULL || len == 0)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    wius_spi_inst_t *instance = (id == WIUS_SPI_INST_0) ? &_wius_spi_0_instance : &_wius_spi_1_instance;

    if (instance->id == WIUS_SPI_INST_0) // GSPI
    {
        bool poll = wait && len <= WIUS_SPI_SHORT_XFER_MAX;
        _wius_spi_prepare_gspi_wait(poll);

        _wius_spi_cs_active(instance->id);
        status = sl_si91x_gspi_send_data(instance->inst.gspi, tx_buf, len);
        if (status != SL_STATUS_OK)
        {
            _wius_spi_0_wait_mode = WIUS_SPI_WAIT_IDLE;
            _wius_spi_cs_inactive(instance->id);
            return status;
        }

        if (poll)
        {
            return _wius_spi_poll_gspi();
        }
    }
    else if (instance->id == WIUS_SPI_INST_1) // SSI
    {
        _wius_spi_cs_active(instance->id);
        status = sl_si91x_ssi_send_data(instance->inst.ssi, tx_buf, len);
        if (status != SL_STATUS_OK)
        {
            _wius_spi_cs_inactive(instance->id);
            return status;
        }
    }

    if (wait)
    {
        LOG_RET_STATUS(wius_spi_await(instance->id));
    }

    return status;
}

sl_status_t wius_spi_await(uint8_t id)
{
    sl_status_t status = SL_STATUS_OK;

    if (id == WIUS_SPI_INST_0) // GSPI
    {
        switch (osSemaphoreAcquire(_wius_spi_0_sem, WIUS_SPI_RX_TIMEOUT))
        {
        case osOK:
            status = _wius_spi_gspi_event_status(_wius_spi_0_event);
            break;
        case osErrorTimeout:
            status = SL_STATUS_TIMEOUT;
            break;
        default:
            status = SL_STATUS_FAIL;
            break;
        }

        _wius_spi_0_wait_mode = WIUS_SPI_WAIT_IDLE;
        _wius_spi_cs_inactive(WIUS_SPI_INST_0);
    }
    else if (id == WIUS_SPI_INST_1) // SSI
    {
        switch (osSemaphoreAcquire(_wius_spi_1_sem, WIUS_SPI_RX_TIMEOUT))
        {
        case osOK:
            status = SL_STATUS_OK;
            break;
        case osErrorTimeout:
            status = SL_STATUS_TIMEOUT;
            break;
        default:
            status = SL_STATUS_FAIL;
            break;
        }

        _wius_spi_cs_inactive(WIUS_SPI_INST_1);
    }
    else
    {
        status = SL_STATUS_INVALID_PARAMETER;
    }

    return status;
}

static void _wius_spi_prepare_gspi_wait(bool poll)
{
    // A late completion from a failed transfer must not satisfy a new await.
    while (osSemaphoreAcquire(_wius_spi_0_sem, 0) == osOK)
        ;

    _wius_spi_0_event = 0;
    _wius_spi_0_complete = false;
    _wius_spi_0_wait_mode = poll ? WIUS_SPI_WAIT_POLL : WIUS_SPI_WAIT_SEMAPHORE;
}

static sl_status_t _wius_spi_poll_gspi(void)
{
    uint32_t start = osKernelGetTickCount();

    while (!_wius_spi_0_complete)
    {
        if ((uint32_t)(osKernelGetTickCount() - start) >= WIUS_SPI_RX_TIMEOUT)
        {
            _wius_spi_0_wait_mode = WIUS_SPI_WAIT_IDLE;
            _wius_spi_cs_inactive(WIUS_SPI_INST_0);
            return SL_STATUS_TIMEOUT;
        }
    }

    sl_status_t status = _wius_spi_gspi_event_status(_wius_spi_0_event);
    _wius_spi_0_wait_mode = WIUS_SPI_WAIT_IDLE;
    _wius_spi_cs_inactive(WIUS_SPI_INST_0);
    return status;
}

static sl_status_t _wius_spi_gspi_event_status(uint32_t event)
{
    if ((event & (SL_GSPI_DATA_LOST | SL_GSPI_MODE_FAULT)) != 0)
    {
        return SL_STATUS_FAIL;
    }

    return (event & SL_GSPI_TRANSFER_COMPLETE) != 0 ? SL_STATUS_OK : SL_STATUS_FAIL;
}

static void _wius_spi_gspi_callback(uint32_t event)
{
    if (_wius_spi_0_wait_mode == WIUS_SPI_WAIT_IDLE)
    {
        return;
    }

    if ((event & (SL_GSPI_TRANSFER_COMPLETE | SL_GSPI_DATA_LOST | SL_GSPI_MODE_FAULT)) != 0)
    {
        _wius_spi_0_event = event;
        _wius_spi_0_complete = true;

        if (_wius_spi_0_wait_mode == WIUS_SPI_WAIT_SEMAPHORE)
        {
            osSemaphoreRelease(_wius_spi_0_sem);
        }
    }
}

static void _wius_spi_ssi_callback(uint32_t event)
{
    if (event == SSI_EVENT_TRANSFER_COMPLETE)
    {
        osSemaphoreRelease(_wius_spi_1_sem);
    }
}
