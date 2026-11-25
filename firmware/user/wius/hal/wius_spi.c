/**
 * @file wius_spi.c
 *
 * @brief WiUS SPI implementation source file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Lisa Maria Odermatt, ETH Zurich
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

wius_spi_inst_t _wius_spi_0_instance = {0};

static void _wius_spi_ssi_callback(uint32_t event);

/*
 * The Si91x SSI high-level configuration API defaults a standard (single-line)
 * master to hardware-controlled SS.  This project routes CS0 through GPIO 53
 * and multiplexes it in the FPGA, so every bus target requires a real
 * software-controlled CS pulse.  In addition, the FPGA's enhanced dual-SPI
 * command configuration leaves state in SPI_CTRLR0 that is not cleared by a
 * normal SSI reconfiguration.  Reset both pieces of state whenever the shared
 * SSI is configured.
 */
static sl_status_t _wius_spi_restore_software_cs_and_raw_framing(wius_spi_inst_t *instance)
{
    if ((instance == NULL) || (instance->inst.ssi == NULL))
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    sl_ssi_driver_t *driver = (sl_ssi_driver_t *)instance->inst.ssi;
    if (driver->Control == NULL)
    {
        return SL_STATUS_INVALID_STATE;
    }

    sl_si91x_ssi_set_slave_number(SSI_SLAVE_0);

    const uint32_t control = SL_SSI_MASTER_ACTIVE |
                             ARM_SPI_SS_MASTER_SW |
                             instance->config.mode |
                             ARM_SPI_DATA_BITS(instance->config.width) |
                             instance->config.transfer_mode;
    if (driver->Control(control, instance->config.freq) != ARM_DRIVER_OK)
    {
        return SL_STATUS_FAIL;
    }

    /* SPI_Command_Configure() used by the FPGA owns these fields.  The normal
     * full-duplex SSI transfer routine does not clear them, so clear all
     * enhanced command/address/dummy state before AFE/TX raw SPI traffic. */
    SSI0->SSIENR = SSI_DISABLE;
    SSI0->SER = 0U;
    SSI0->CTRLR0_b.SPI_FRF = 0U;             /* standard single-line SPI */
    SSI0->SPI_CTRLR0_b.TRANS_TYPE = 0U;
    SSI0->SPI_CTRLR0_b.INST_L = 0U;
    SSI0->SPI_CTRLR0_b.ADDR_L = 0U;
    SSI0->SPI_CTRLR0_b.WAIT_CYCLES = 0U;
    SSI0->CTRLR1 = 0U;
    SSI0->DMACR = 0U;

    if (instance->config.cs_mode == WIUS_SPI_CS_SW)
    {
        /* The CMSIS Control call above changes CS0 back to GPIO ownership.
         * Drive the physical active-low GPIO 53 high before any transaction. */
        wius_gpio_config(instance->cs);
        wius_gpio_put(instance->cs, !instance->config.cs_polarity);
    }

    return SL_STATUS_OK;
}

wius_spi_inst_t wius_spi_get_instance(uint8_t id)
{
    if (id != WIUS_SPI_INST_0)
    {
        return (wius_spi_inst_t){0};
    }

    return _wius_spi_0_instance;
}

sl_status_t wius_spi_init(uint8_t id, wius_spi_config_t *config)
{
    sl_status_t status = SL_STATUS_OK;

    if ((id != WIUS_SPI_INST_0) || (config == NULL))
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    wius_spi_inst_t *instance = &_wius_spi_0_instance;

    instance->id = id;
    instance->config = *config;
    if (instance->config.cs_mode == WIUS_SPI_CS_SW)
    {
        instance->cs = WIUS_GPIO_OUTPUT(instance->config.cs_pin);
        wius_gpio_config(instance->cs);
        wius_gpio_put(instance->cs, !instance->config.cs_polarity);
    }

    LOG_RET_STATUS(sl_si91x_ssi_init(SL_SSI_MASTER_ACTIVE, &instance->inst.ssi));

    sl_ssi_control_config_t ssi_config = {
        .baud_rate = instance->config.freq,
        .bit_width = instance->config.width,
        .clock_mode = instance->config.mode,
        .device_mode = SL_SSI_MASTER_ACTIVE,
        .receive_sample_delay = instance->config.rx_sample_delay,
        .transfer_mode = instance->config.transfer_mode,
    };
    LOG_RET_STATUS(sl_si91x_ssi_set_configuration(instance->inst.ssi, &ssi_config, SSI_SLAVE_0));
    LOG_RET_STATUS(_wius_spi_restore_software_cs_and_raw_framing(instance));

    _wius_spi_0_sem = osSemaphoreNew(1, 0, NULL);
    if (_wius_spi_0_sem == NULL)
    {
        return SL_STATUS_ALLOCATION_FAILED;
    }

    LOG_RET_STATUS(sl_si91x_ssi_register_event_callback(instance->inst.ssi, _wius_spi_ssi_callback));

    return status;
}

sl_status_t wius_spi_reconfigure(uint8_t id, const wius_spi_config_t *config)
{
    if ((id != WIUS_SPI_INST_0) || (config == NULL) || (_wius_spi_0_instance.inst.ssi == NULL))
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    sl_ssi_control_config_t ssi_config = {
        .baud_rate = config->freq,
        .bit_width = config->width,
        .clock_mode = config->mode,
        .device_mode = SL_SSI_MASTER_ACTIVE,
        .receive_sample_delay = config->rx_sample_delay,
        .transfer_mode = config->transfer_mode,
    };

    sl_status_t status = sl_si91x_ssi_set_configuration(_wius_spi_0_instance.inst.ssi,
                                                         &ssi_config,
                                                         SSI_SLAVE_0);
    if (status == SL_STATUS_OK)
    {
        _wius_spi_0_instance.config = *config;
        status = _wius_spi_restore_software_cs_and_raw_framing(&_wius_spi_0_instance);
    }

    return status;
}

sl_status_t wius_spi_set_cs(uint8_t id, bool active)
{
    if (id != WIUS_SPI_INST_0)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    wius_spi_inst_t *instance = &_wius_spi_0_instance;

    if (instance->config.cs_mode == WIUS_SPI_CS_SW)
    {
        sl_ssi_driver_t *driver = (sl_ssi_driver_t *)instance->inst.ssi;
        if ((driver == NULL) || (driver->Control == NULL))
        {
            return SL_STATUS_INVALID_STATE;
        }

        uint32_t state = active ? ARM_SPI_SS_ACTIVE : ARM_SPI_SS_INACTIVE;
        if (driver->Control(ARM_SPI_CONTROL_SS, state) != ARM_DRIVER_OK)
        {
            return SL_STATUS_FAIL;
        }

        return SL_STATUS_OK;
    }

    if (instance->config.cs_mode == WIUS_SPI_CS_HW)
    {
        sl_ssi_driver_t *driver = (sl_ssi_driver_t *)instance->inst.ssi;
        uint32_t state = active ? ARM_SPI_SS_ACTIVE : ARM_SPI_SS_INACTIVE;

        if ((driver == NULL) || (driver->Control == NULL))
        {
            return SL_STATUS_INVALID_STATE;
        }
        if (driver->Control(ARM_SPI_CONTROL_SS, state) != ARM_DRIVER_OK)
        {
            return SL_STATUS_FAIL;
        }
    }

    return SL_STATUS_OK;
}

static sl_status_t _wius_spi_transfer(uint8_t id, const uint8_t *tx_buf, uint8_t *rx_buf,
                                      size_t len, bool wait)
{
    sl_status_t status = SL_STATUS_OK;

    if (id != WIUS_SPI_INST_0 || tx_buf == NULL || len == 0U)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    wius_spi_inst_t *instance = &_wius_spi_0_instance;
    LOG_RET_STATUS(wius_spi_clear_completion(id));

    sl_si91x_ssi_set_slave_number(SSI_SLAVE_0);

    LOG_RET_STATUS(wius_spi_set_cs(instance->id, true));
    delay_ns(instance->config.cs_assert_delay_ns);

    status = rx_buf == NULL
        ? sl_si91x_ssi_send_data(instance->inst.ssi, tx_buf, len)
        : sl_si91x_ssi_transfer_data(instance->inst.ssi, (uint8_t *)tx_buf, rx_buf, len);
    if (status != SL_STATUS_OK)
    {
        (void)wius_spi_set_cs(instance->id, false);

        return status;
    }

    if (wait)
    {
        LOG_RET_STATUS(wius_spi_await(instance->id));
    }

    return status;
}

sl_status_t wius_spi_xfer(uint8_t id, uint8_t *tx_buf, uint8_t *rx_buf, size_t len, bool wait)
{
    if (rx_buf == NULL)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }
    return _wius_spi_transfer(id, tx_buf, rx_buf, len, wait);
}

sl_status_t wius_spi_send(uint8_t id, const uint8_t *tx_buf, size_t len, bool wait)
{
    return _wius_spi_transfer(id, tx_buf, NULL, len, wait);
}

sl_status_t wius_spi_await(uint8_t id)
{
    if (id != WIUS_SPI_INST_0)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    sl_status_t status = wius_spi_await_completion(id, 1000U);
    delay_ns(_wius_spi_0_instance.config.cs_deassert_delay_ns);
    (void)wius_spi_set_cs(WIUS_SPI_INST_0, false);
    return status;
}

sl_status_t wius_spi_clear_completion(uint8_t id)
{
    if ((id != WIUS_SPI_INST_0) || (_wius_spi_0_sem == NULL))
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    while (osSemaphoreAcquire(_wius_spi_0_sem, 0U) == osOK)
    {
    }

    return SL_STATUS_OK;
}

sl_status_t wius_spi_await_completion(uint8_t id, uint32_t timeout_ms)
{
    if ((id != WIUS_SPI_INST_0) || (_wius_spi_0_sem == NULL))
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    uint32_t ticks = (uint32_t)(((uint64_t)timeout_ms * osKernelGetTickFreq() + 999U) / 1000U);
    osStatus_t status = osSemaphoreAcquire(_wius_spi_0_sem, ticks);
    if (status == osOK)
    {
        return SL_STATUS_OK;
    }

    // Stop DMA before the caller can reuse its transmit or receive buffer.
    wius_spi_abort(id);
    return status == osErrorTimeout ? SL_STATUS_TIMEOUT : SL_STATUS_FAIL;
}

void wius_spi_abort(uint8_t id)
{
    if (id == WIUS_SPI_INST_0 && _wius_spi_0_instance.inst.ssi != NULL)
    {
        sl_ssi_driver_t *driver = (sl_ssi_driver_t *)_wius_spi_0_instance.inst.ssi;
        (void)driver->Control(ARM_SPI_ABORT_TRANSFER, 0U);
    }
}

static void _wius_spi_ssi_callback(uint32_t event)
{
    if (event == SSI_EVENT_TRANSFER_COMPLETE)
    {
        osSemaphoreRelease(_wius_spi_0_sem);
    }
}
