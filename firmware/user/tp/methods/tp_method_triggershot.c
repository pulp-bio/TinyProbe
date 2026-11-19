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
#include "tp_spi.h"
#include "regmap_fpga.h"

#define TP_NO_CALLBACK UINT16_MAX

static sl_status_t _tp_wait_results_ready(bool external_mode)
{
    const uint32_t timeout_ms = external_mode ? 60000U : 1000U;
    const uint32_t start = time_ms();
    do
    {
        uint32_t value = 0U;
        sl_status_t status = tp_fpga_read_reg(REGMAP_FPGA_ADDR_TRANSPORT_STATUS, &value);
        if (status != SL_STATUS_OK)
        {
            return status;
        }
        // The interrupt can wake this task early. Wait for the sticky results-ready flag.
        if (REGMAP_FPGA_TRANSPORT_STATUS_GET_PAGE_TAG(value) == REGMAP_FPGA_TRANSPORT_STATUS_PAGE_TAG_RESULTS &&
            REGMAP_FPGA_TRANSPORT_STATUS_GET_READY(value) != 0U)
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
        sl_status_t status = tp_fpga_read_reg(REGMAP_FPGA_ADDR_TRANSPORT_STATUS, &value);
        if (status != SL_STATUS_OK)
        {
            return status;
        }
        if (REGMAP_FPGA_TRANSPORT_STATUS_GET_READY(value) != 0U)
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
    sl_status_t status = tp_fpga_write_reg(REGMAP_FPGA_AFE_TX_RST_REG_AFE_GPWD_SRC_MASK,
                                          REGMAP_FPGA_ADDR_AFE_TX_RST_REG);
    tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, true);
    return status;
}

static sl_status_t _tp_transmit_lane_packets(uint32_t shot, uint16_t num_lanes,
                                              uint16_t callback_id, bool *callback_powered_down)
{
    // DMA starts at the payload. Keep its buffer aligned independently of the UDP header.
    _Alignas(uint32_t) static uint8_t spi_rx[TP_FIFO_READ_SIZE];

    for (uint16_t packet = 0; packet < num_lanes; packet++)
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

static sl_status_t _tp_acquire_shots(const methods_triggershot_args *args, uint16_t num_lanes,
                                     bool external_mode, uint32_t irq_config)
{
    sl_status_t status = SL_STATUS_OK;
    const uint32_t stream_config = REGMAP_FPGA_EXT_INT_TRIG_REG_SET_STATUS_CONTROL(
        irq_config, REGMAP_FPGA_EXT_INT_TRIG_REG_STATUS_CONTROL_STREAM);
    const uint32_t result_config = REGMAP_FPGA_EXT_INT_TRIG_REG_SET_STATUS_CONTROL(
        irq_config, REGMAP_FPGA_EXT_INT_TRIG_REG_STATUS_CONTROL_RESULTS);
    bool callback_powered_down = false;

    for (uint32_t shot = 0; shot < args->num_shots; shot++)
    {
        status = tp_fpga_reset_multififo();
        if (status != SL_STATUS_OK) break;

        while (osSemaphoreAcquire(sem_fpga, 0U) == osOK)
        {
        }
        status = tp_fpga_write_reg(result_config, REGMAP_FPGA_ADDR_EXT_INT_TRIG_REG);
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
            status = tp_fpga_write_reg(REGMAP_FPGA_AFE_TX_RST_REG_AFE_GPWD_SRC_MASK |
                                       REGMAP_FPGA_AFE_TX_RST_REG_AFE_GPWD_CTRL_MASK,
                                       REGMAP_FPGA_ADDR_AFE_TX_RST_REG);
            if (status != SL_STATUS_OK) break;
            tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, false);
            callback_powered_down = true;
        }

        // Read the transport status layout while waiting for the stream FIFO to fill.
        status = tp_fpga_write_reg(stream_config, REGMAP_FPGA_ADDR_EXT_INT_TRIG_REG);
        if (status != SL_STATUS_OK) break;
        status = tp_fpga_en_read();
        if (status != SL_STATUS_OK) break;
        status = _tp_wait_stream_ready();
        if (status != SL_STATUS_OK) break;
        status = _tp_transmit_lane_packets(shot, num_lanes, args->callback_id, &callback_powered_down);
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
    if (status == SL_STATUS_OK) status = tp_fpga_read_reg(REGMAP_FPGA_ADDR_LVDS_CH_EN, &capture_config);
    if (status == SL_STATUS_OK) status = tp_fpga_read_reg(REGMAP_FPGA_ADDR_WAVEFORM_GEN_REG_5, &mode);
    if (status == SL_STATUS_OK) status = tp_fpga_read_reg(REGMAP_FPGA_ADDR_EXT_INT_TRIG_REG, &irq_config);
    if (status != SL_STATUS_OK)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    const uint32_t lane_mask = REGMAP_FPGA_LVDS_CH_EN_GET_LVDS_CH_EN(capture_config);
    const uint16_t available_lanes = (uint16_t)__builtin_popcount(lane_mask);
    const uint32_t num_lanes = args->num_packets == 0U ? available_lanes : args->num_packets;
    if (num_lanes == 0U || num_lanes > available_lanes ||
        (args->callback_id != TP_NO_CALLBACK && args->callback_id >= num_lanes))
    {
        return methods_status_INVALID_ARGUMENT;
    }

    const bool external_mode = REGMAP_FPGA_WAVEFORM_GEN_REG_5_GET_EXTERNAL_ACQUISITION(mode) != 0U;
    uint32_t capture_irq_config = REGMAP_FPGA_EXT_INT_TRIG_REG_SET_MIM(
        irq_config, REGMAP_FPGA_EXT_INT_TRIG_REG_MIM_MCU_INT_FIFO_WR_DONE);
    if (external_mode)
    {
        capture_irq_config = REGMAP_FPGA_EXT_INT_TRIG_REG_SET_EIT(
            capture_irq_config, REGMAP_FPGA_EXT_INT_TRIG_REG_EIT_EXTERNAL_TRIGGER);
    }
    status = _tp_acquire_shots(args, (uint16_t)num_lanes, external_mode, capture_irq_config);
    sl_status_t restore_status = tp_fpga_write_reg(irq_config, REGMAP_FPGA_ADDR_EXT_INT_TRIG_REG);
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
