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
 * @author Lisa Maria Odermatt, ETH Zurich
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

#define TP_FPGA_CAPTURE_CONFIG_REG 2U
#define TP_FPGA_MODE_REG 12U
#define TP_FPGA_IRQ_CONFIG_REG 13U
#define TP_FPGA_STATUS_REG 15U
#define TP_FPGA_EXTERNAL_MODE (1UL << 25U)
#define TP_FPGA_IRQ_SELECT_MASK (3UL << 1U)
#define TP_FPGA_STATUS_PAGE_MASK (0xFF800000UL)
#define TP_FPGA_RESULTS_STATUS_PAGE (1UL << 27U)
#define TP_FPGA_RESULT_READY 1U
#define TP_FPGA_STREAM_READY 1U
#define TP_NO_CALLBACK UINT16_MAX

static sl_status_t _tp_wait_results_ready(bool external_mode)
{
    const uint32_t timeout_ms = external_mode ? 60000U : 1000U;
    const uint32_t start = time_ms();
    do
    {
        uint32_t value = 0U;
        sl_status_t status = tp_fpga_read_reg(TP_FPGA_STATUS_REG, &value);
        if (status != SL_STATUS_OK)
        {
            return status;
        }
        // The interrupt can wake this task early. Wait for the sticky results-ready flag.
        if ((value >> 24U) == 0xD4U && (value & TP_FPGA_RESULT_READY) != 0U)
        {
            return SL_STATUS_OK;
        }
        const uint32_t poll_ticks = (osKernelGetTickFreq() + 9U) / 10U;
        (void)osSemaphoreAcquire(sem_fpga, poll_ticks);
    } while (time_ms() - start < timeout_ms);

    log_error("Timed out waiting for FPGA acquisition results");
    return SL_STATUS_TIMEOUT;
}

static sl_status_t _tp_wait_stream_ready(void)
{
    const uint32_t start = time_ms();
    do
    {
        uint32_t value = 0U;
        sl_status_t status = tp_fpga_read_reg(TP_FPGA_STATUS_REG, &value);
        if (status != SL_STATUS_OK)
        {
            return status;
        }
        if ((value & TP_FPGA_STREAM_READY) != 0U)
        {
            return SL_STATUS_OK;
        }
        delay_ms(1U);
    } while (time_ms() - start < 1000U);

    log_error("Timed out waiting for FPGA stream data");
    return SL_STATUS_TIMEOUT;
}

static sl_status_t _tp_restore_callback_power(void)
{
    sl_status_t status = tp_fpga_write_reg(16U, 10U);
    tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, true);
    return status;
}

static sl_status_t _tp_transmit_packages(uint32_t shot, uint16_t num_packets,
                                         uint16_t callback_id, bool *callback_powered_down)
{
    // DMA starts at the payload. Keep its buffer aligned independently of the UDP header.
    _Alignas(uint32_t) static uint8_t spi_rx[TP_FIFO_READ_SIZE];

    for (uint16_t packet = 0; packet < num_packets; packet++)
    {
        sl_status_t status = tp_fpga_read_fifo(spi_rx, sizeof(spi_rx));
        if (status != SL_STATUS_OK)
        {
            return status;
        }

        tp_buffer_slot_t *slot = tp_buffer_claim_writing(&tp_buf);
        if (slot == NULL)
        {
            return SL_STATUS_TIMEOUT;
        }

        slot->data[0] = (uint8_t)shot;
        slot->data[1] = (uint8_t)packet;
        memcpy(slot->data + 2, spi_rx, sizeof(spi_rx));
        slot->length = TP_BUFFER_SIZE;
        tp_buffer_return_writing(&tp_buf, slot);

        if (packet == callback_id)
        {
            status = _tp_restore_callback_power();
            if (status != SL_STATUS_OK)
            {
                return status;
            }
            *callback_powered_down = false;
        }
    }
    return SL_STATUS_OK;
}

static sl_status_t _tp_acquire_shots(const methods_triggershot_args *args, uint16_t num_packets,
                                     bool external_mode, uint32_t irq_config)
{
    sl_status_t status = SL_STATUS_OK;
    const uint32_t stream_config = irq_config & ~TP_FPGA_STATUS_PAGE_MASK;
    const uint32_t result_config = stream_config | TP_FPGA_RESULTS_STATUS_PAGE;
    bool callback_powered_down = false;

    for (uint32_t shot = 0; shot < args->num_shots; shot++)
    {
        status = tp_fpga_reset_multififo();
        if (status != SL_STATUS_OK) break;

        while (osSemaphoreAcquire(sem_fpga, 0U) == osOK)
        {
        }
        status = tp_fpga_write_reg(result_config, TP_FPGA_IRQ_CONFIG_REG);
        if (status != SL_STATUS_OK) break;

        if (args->software_trigger || external_mode)
        {
            status = tp_fpga_send_start();
            if (status != SL_STATUS_OK) break;
        }
        status = _tp_wait_results_ready(external_mode);
        if (status != SL_STATUS_OK) break;

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

        if (args->callback_id != TP_NO_CALLBACK)
        {
            status = tp_fpga_write_reg(48U, 10U);
            if (status != SL_STATUS_OK) break;
            tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, false);
            callback_powered_down = true;
        }

        // Read the transport status layout while waiting for the stream FIFO to fill.
        status = tp_fpga_write_reg(stream_config, TP_FPGA_IRQ_CONFIG_REG);
        if (status != SL_STATUS_OK) break;
        status = tp_fpga_en_read();
        if (status != SL_STATUS_OK) break;
        status = _tp_wait_stream_ready();
        if (status != SL_STATUS_OK) break;
        status = _tp_transmit_packages(shot, num_packets, args->callback_id, &callback_powered_down);
        if (status != SL_STATUS_OK) break;
    }

    if (callback_powered_down)
    {
        LOG_STATUS(_tp_restore_callback_power());
    }
    sl_status_t reset_status = tp_fpga_reset_multififo();
    return status == SL_STATUS_OK ? reset_status : status;
}

methods_status tp_method_triggershot(const methods_triggershot_args *args, void *userdata)
{
    UNUSED(userdata);
    if (args->num_shots == 0U || args->num_shots > 256U)
    {
        return methods_status_INVALID_ARGUMENT;
    }

    uint32_t capture_config = 0U;
    uint32_t mode = 0U;
    uint32_t irq_config = 0U;
    sl_status_t status = tp_spi_select(TP_MUX_FPGA);
    if (status == SL_STATUS_OK) status = tp_fpga_read_reg(TP_FPGA_CAPTURE_CONFIG_REG, &capture_config);
    if (status == SL_STATUS_OK) status = tp_fpga_read_reg(TP_FPGA_MODE_REG, &mode);
    if (status == SL_STATUS_OK) status = tp_fpga_read_reg(TP_FPGA_IRQ_CONFIG_REG, &irq_config);
    if (status != SL_STATUS_OK)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    const uint16_t available_packets = (uint16_t)__builtin_popcount(capture_config & UINT16_MAX);
    const uint32_t num_packets = args->num_packets == 0U ? available_packets : args->num_packets;
    if (num_packets == 0U || num_packets > available_packets ||
        (args->callback_id != TP_NO_CALLBACK && args->callback_id >= num_packets))
    {
        return methods_status_INVALID_ARGUMENT;
    }

    const bool external_mode = (mode & TP_FPGA_EXTERNAL_MODE) != 0U;
    uint32_t capture_irq_config = irq_config & ~TP_FPGA_IRQ_SELECT_MASK;
    if (external_mode)
    {
        capture_irq_config |= 1U; // Enable the external trigger input.
    }
    status = _tp_acquire_shots(args, (uint16_t)num_packets, external_mode, capture_irq_config);
    sl_status_t restore_status = tp_fpga_write_reg(irq_config, TP_FPGA_IRQ_CONFIG_REG);
    if (status == SL_STATUS_OK)
    {
        status = restore_status;
    }
    if (status != SL_STATUS_OK)
    {
        LOG_STATUS(status);
        return status == SL_STATUS_TIMEOUT ? methods_status_TIMEOUT : methods_status_UNKNOWN_ERROR;
    }
    return methods_status_OK;
}
