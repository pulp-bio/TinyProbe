/**
 * @file tp_command_triggershot.c
 *
 * @brief TinyProbe AFE write command implementation file
 *
 * @date 08.09.2025
 * @copyright ETH Zurich. All rights reserved.
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

#include "tp_command_triggershot.h"

#include "SEGGER_RTT.h"

#include "tp.h"
#include "tp_fpga.h"
#include "tp_power.h"
#include "wius_spi.h"

// #define PUTC_FAST(ch) SEGGER_RTT_PutChar(0, ch);
#define PUTC_FAST(ch)

volatile uint32_t count_interrupt_received = 0;
volatile uint32_t count_call_transmit = 0;
volatile uint32_t count_called_transmit = 0;
volatile uint32_t count_start_transmit = 0;
volatile uint32_t count_done = 0;

sl_status_t _tp_transmit_packages(void);

sl_status_t tp_trigger_shot(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;
    sl_status_t status = SL_STATUS_OK;

    uint32_t n_shots = GET(args, uint16_t, 0);
    n_packs_to_read = GET(args, uint16_t, 2);
    uint32_t dcdc_delay_ns = (uint32_t)GET(args, uint8_t, 4) * 100;
    uint32_t read_delay_ns = (uint32_t)GET(args, uint8_t, 5) * 1000;
    cb_pack_id = GET(args, uint16_t, 6);
    uint8_t software_trig = GET(args, uint8_t, 8);
    uint8_t dcdc_pwd_at_rx = GET(args, uint8_t, 9);

    LOG_I("Triggering %lu shots with %u packets each", n_shots, n_packs_to_read);
    // LOG_I("-> %u packets with %u packets concatenated", (n_packs_to_read + (TP_UDP_PACKET_AMT - 1)) / TP_UDP_PACKET_AMT, TP_UDP_PACKET_AMT);

    // LOG_I("dcdc_delay_ns=%luns, read_delay_ns=%luns, software_trig=%u, dcdc_pwd_at_rx=%u", dcdc_delay_ns, read_delay_ns, software_trig, dcdc_pwd_at_rx);

    //    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_HIGH));
    //    CHECK_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_HIGHSPEED));
    //    LOG_D("High speed mode activated");

    // Empty FPGA semaphore
    while (osSemaphoreAcquire(sem_fpga, 0) == osOK)
        ;

    CHECK_STATUS(tp_fpga_reset_multififo());
    CHECK_STATUS(tp_fpga_empty_tx());

    if (software_trig)
    {
        CHECK_STATUS(tp_fpga_send_start());
        LOG_D("Sent start command");
    }

    for (uint32_t i = 0; i < n_shots; i++)
    {
#if !TP_TEST_MODE
        if (osSemaphoreAcquire(sem_fpga, 1000) != osOK)
        {
            LOG_E("Error waiting for FIFO data ready flag");
            continue;
        }
        count_interrupt_received = DWT->CYCCNT;
#else
        // delay_ms(1);
        count_interrupt = DWT->CYCCNT;

        count_interrupt_received = DWT->CYCCNT;
#endif

        delay_ns(dcdc_delay_ns);

        if (dcdc_pwd_at_rx)
        {
            tp_power_set(TP_POWER_DOMAIN_POS_HV, false);
            tp_power_set(TP_POWER_DOMAIN_NEG_HV, false);
        }

        delay_ns(read_delay_ns);

        if (dcdc_pwd_at_rx)
        {
            tp_power_set(TP_POWER_DOMAIN_POS_HV, true);
            tp_power_set(TP_POWER_DOMAIN_NEG_HV, true);
        }

        if (cb_pack_id != 65535)
        {
            // Enable AFE Global power down
            tp_fpga_write_reg_safe(48, 10);
            // Disable LVDS IO bank of the FPGA
            tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, false);
        }

        tp_fpga_en_read();

        delay_ns(2400);

        count_call_transmit = DWT->CYCCNT;

        _tp_transmit_packages();

        CHECK_STATUS(tp_fpga_reset_multififo());
    }

    //    CHECK_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_LOWPOWER));
    //    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_LOW));
    //    LOG_D("Low power mode activated");

    LOG_I("Done");

    return SL_STATUS_OK;
}

sl_status_t _tp_transmit_packages(void)
{
    sl_status_t status = SL_STATUS_OK;

    count_called_transmit = DWT->CYCCNT;

    tp_buffer_slot_t *slot_spi = tp_buffer_claim_writing(&tp_buf);
    if (NULL == slot_spi)
    {
        LOG_W("Timeout claiming initial buffer for write");
        return SL_STATUS_FAIL;
    }

    PUTC_FAST('w');

    uint8_t tx_dummy[TP_BUFFER_SIZE] = {0};
    status = tp_fpga_read_fifo(tx_dummy, slot_spi->data, TP_BUFFER_SIZE, false);
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error starting initial SPI recv: 0x%04X", (unsigned)status);
        return status;
    }

    PUTC_FAST('f');

    count_start_transmit = DWT->CYCCNT;

    uint16_t n_packs_to_read_div = (n_packs_to_read + (TP_UDP_PACKET_AMT - 1)) / TP_UDP_PACKET_AMT;

    for (uint16_t i = 0; i < n_packs_to_read_div; i++)
    {
        CHECK_STATUS(wius_spi_await(WIUS_SPI_INST_0));

        PUTC_FAST('a');

        slot_spi->length = TP_BUFFER_SIZE;
        tp_buffer_return_writing(&tp_buf, slot_spi);

        PUTC_FAST('r');
        PUTC_FAST('\n');

        if (i == (uint16_t)(cb_pack_id / TP_UDP_PACKET_AMT))
        {
            tp_fpga_write_reg_safe(16, 10); // Disable AFE Global power down
            tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, true);
            LOG_D("Callback packet %u sent, AFE powered on", i);
        }

        if (i != n_packs_to_read_div - 1)
        {
            slot_spi = tp_buffer_claim_writing(&tp_buf);
            if (NULL == slot_spi)
            {
                LOG_E("Error claiming buffer for write");
                return SL_STATUS_FAIL;
            }

            PUTC_FAST('w');

            status = tp_fpga_read_fifo(tx_dummy, slot_spi->data, TP_BUFFER_SIZE, false);
            if (SL_STATUS_OK != status)
            {
                LOG_E("Error starting SPI recv: 0x%04X", (unsigned)status);
                return status;
            }

            PUTC_FAST('f');
        }
    }

    count_done = DWT->CYCCNT;

    // count_interrupt_received -= count_interrupt;
    // count_call_transmit -= count_interrupt;
    // count_called_transmit -= count_interrupt;
    // count_start_transmit -= count_interrupt;
    // count_done -= count_interrupt;

    // LOG_I("Cycle counts:");
    // LOG_I(" Interrupt to received: %lu", count_interrupt_received);
    // LOG_I(" Call Transmit Packets: %lu", count_call_transmit);
    // LOG_I(" Start of Transmit pa.: %lu", count_called_transmit);
    // LOG_I(" Transmit packets done: %lu", count_done);

    // uint32_t core_clock_mhz = core_clock_hz() / 1e6;

    // count_interrupt_received /= core_clock_mhz;
    // count_call_transmit /= core_clock_mhz;
    // count_called_transmit /= core_clock_mhz;
    // count_start_transmit /= core_clock_mhz;
    // count_done /= core_clock_mhz;

    // LOG_I("Time [us]:");
    // LOG_I(" Interrupt to received: %lu", count_interrupt_received);
    // LOG_I(" Call Transmit Packets: %lu", count_call_transmit);
    // LOG_I(" Start of Transmit pa.: %lu", count_called_transmit);
    // LOG_I(" Transmit Packets whi.: %lu", count_start_transmit);
    // LOG_I(" Transmit packets done: %lu", count_done);

    return status;
}