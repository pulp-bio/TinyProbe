/**
 * @file tp_method_triggershot.c
 *
 * @brief TinyProbe Trigger Shot method implementation file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 *
 * @ingroup tinyprobe_methods
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

#include "tp_method_triggershot.h"

#include "tp.h"
#include "tp_fpga.h"
#include "tp_power.h"
#include "wius_spi.h"

static uint8_t tx_dummy[TP_BUFFER_SIZE] = {0};

static sl_status_t _tp_transmit_packages(uint32_t shot_index, uint16_t num_packets,
                                         uint16_t callback_id, bool *callback_powered_down);
static sl_status_t _tp_restore_callback_power(bool *callback_powered_down);

methods_status tp_method_triggershot(const methods_triggershot_args *args, void *userdata)
{
    UNUSED(userdata);

    sl_status_t status = SL_STATUS_OK;
    bool callback_powered_down = false;

    if (args->num_shots == 0 || args->num_shots > 256 ||
        args->num_packets == 0 || args->num_packets > 256 ||
        (args->callback_id != 65535 && args->callback_id >= args->num_packets))
    {
        return methods_status_INVALID_ARGUMENT;
    }

    // log_info("Triggering %lu shots with %u packets each", args->num_shots, args->num_packets);
    // log_info("dcdc_off_delay_ns=%luns, read_fifo_delay_ns=%luns, sw_trigger=%u, dcdc_pwd_at_rx=%u", dcdc_off_delay_ns, read_fifo_delay_ns, sw_trigger, dcdc_pwd_at_rx);

    // log_trace("Resetting FPGA multififo");
    status = tp_fpga_reset_multififo();
    if (SL_STATUS_OK != status)
    {
        goto error;
    }

    // log_trace("Emptying FPGA TX FIFO");
    status = tp_fpga_empty_tx();
    if (SL_STATUS_OK != status)
    {
        goto error;
    }

    // Empty FPGA semaphore
    while (osSemaphoreAcquire(sem_fpga, 0) == osOK)
        ;

    if (args->software_trigger)
    {
        // log_trace("Sending start command to FPGA");
        status = tp_fpga_send_start();
        if (SL_STATUS_OK != status)
        {
            goto error;
        }
        // log_debug("Sent start method");
    }

    // log_trace("Entering shot loop");
    for (uint32_t i = 0; i < args->num_shots; i++)
    {
#if !TP_TEST_MODE
        if (osSemaphoreAcquire(sem_fpga, 1000) != osOK)
        {
            log_error("Error waiting for FIFO data ready flag");
            status = SL_STATUS_TIMEOUT;
            goto error;
        }
#endif

        delay_ns(args->delay_dcdc_off_ns);

        if (args->pwd_dcdc_at_rx)
        {
            tp_power_set(TP_POWER_DOMAIN_POS_HV, false);
            tp_power_set(TP_POWER_DOMAIN_NEG_HV, false);
        }

        delay_ns(args->delay_read_fifo_ns);

        if (args->pwd_dcdc_at_rx)
        {
            tp_power_set(TP_POWER_DOMAIN_POS_HV, true);
            tp_power_set(TP_POWER_DOMAIN_NEG_HV, true);
        }

        if (args->callback_id != 65535)
        {
            // Enable AFE Global power down
            status = tp_fpga_write_reg(48, 10);
            if (SL_STATUS_OK != status)
            {
                goto error;
            }
            // Disable LVDS IO bank of the FPGA
            tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, false);
            callback_powered_down = true;
        }

        status = tp_fpga_en_read();
        if (SL_STATUS_OK != status)
        {
            goto error;
        }

        // Wait 24 clock cycles of 10 MHz clock
        // It is worst case maximum time needed for the internal IP
        // To read the data from the Core FIFO and push it into the SPI TX buffer.
        delay_ns(2400);

        status = _tp_transmit_packages(i, (uint16_t)args->num_packets,
                                       (uint16_t)args->callback_id, &callback_powered_down);
        if (SL_STATUS_OK != status)
        {
            goto error;
        }

        status = tp_fpga_reset_multififo();
        if (SL_STATUS_OK != status)
        {
            goto error;
        }
    }

    return methods_status_OK;

error:
    if (callback_powered_down)
    {
        sl_status_t restore_status = _tp_restore_callback_power(&callback_powered_down);
        if (SL_STATUS_OK == status)
        {
            status = restore_status;
        }
        else if (SL_STATUS_OK != restore_status)
        {
            LOG_STATUS(restore_status);
        }
    }

    LOG_STATUS(status);
    return methods_status_UNKNOWN_ERROR;
}

static sl_status_t _tp_transmit_packages(uint32_t shot_index, uint16_t num_packets,
                                         uint16_t callback_id, bool *callback_powered_down)
{
    sl_status_t status = SL_STATUS_OK;

    tp_buffer_slot_t *slot_spi = tp_buffer_claim_writing(&tp_buf);
    if (NULL == slot_spi)
    {
        log_warn("Timeout claiming initial buffer for write");
        return SL_STATUS_FAIL;
    }

    status = tp_fpga_read_fifo(tx_dummy, slot_spi->data, TP_BUFFER_SIZE, false);
    if (SL_STATUS_OK != status)
    {
        log_error("Error starting initial SPI recv: 0x%04X", (unsigned)status);
        return status;
    }

    uint16_t num_packet_groups =
        (num_packets + (TP_UDP_PACKET_AMT - 1)) / TP_UDP_PACKET_AMT;

    for (uint16_t packet_group = 0; packet_group < num_packet_groups; packet_group++)
    {
        status = wius_spi_await(WIUS_SPI_INST_0);
        if (SL_STATUS_OK != status)
        {
            log_error("Error waiting for SPI recv complete: 0x%04X", (unsigned)status);
            tp_buffer_return_writing(&tp_buf, slot_spi);
            return status;
        }

        slot_spi->data[0] = shot_index & 0xFF;
        slot_spi->data[1] = packet_group & 0xFF;
        slot_spi->length = TP_BUFFER_SIZE;
        tp_buffer_return_writing(&tp_buf, slot_spi);

        if (callback_id != 65535 &&
            packet_group == (uint16_t)(callback_id / TP_UDP_PACKET_AMT))
        {
            status = _tp_restore_callback_power(callback_powered_down);
            if (SL_STATUS_OK != status)
            {
                return status;
            }
        }

        if (packet_group != num_packet_groups - 1)
        {
            slot_spi = tp_buffer_claim_writing(&tp_buf);
            if (NULL == slot_spi)
            {
                log_error("Error claiming buffer for write");
                return SL_STATUS_FAIL;
            }

            status = tp_fpga_read_fifo(tx_dummy, slot_spi->data, TP_BUFFER_SIZE, false);
            if (SL_STATUS_OK != status)
            {
                log_error("Error starting SPI recv: 0x%04X", (unsigned)status);
                return status;
            }
        }
    }

    return status;
}

static sl_status_t _tp_restore_callback_power(bool *callback_powered_down)
{
    if (!*callback_powered_down)
    {
        return SL_STATUS_OK;
    }

    sl_status_t status = tp_fpga_write_reg(16, 10);
    if (SL_STATUS_OK != status)
    {
        return status;
    }

    tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, true);
    *callback_powered_down = false;

    return SL_STATUS_OK;
}
