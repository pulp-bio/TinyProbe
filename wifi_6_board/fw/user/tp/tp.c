/**
 * @file tp.c
 *
 * @brief TinyProbe main source file
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

#include "tp.h"

#include "sl_si91x_power_manager.h"

#include "tp_command.h"
#include "tp_mux.h"
#include "tp_fpga.h"
#include "tp_afe.h"
#include "tp_tx.h"
#include "tp_power.h"
#include "tp_buffer.h"
#include "wius_power.h"
#include "wius_wifi.h"
#include "wius_spi.h"
#include "wius_udp.h"
#include "wius_gpio.h"

#define GET(args, type, pos) (*(type *)(args + pos))

wius_gpio_t int_pin = WIUS_GPIO_UULP_INPUT(TP_GPIO_INT);
wius_gpio_t reset_pin = WIUS_GPIO_ULP_OUTPUT(TP_GPIO_RESET);

wius_spi_inst_t spi_inst;
wius_spi_config_t spi_config = {
    .cs_mode = (WIUS_SPI_EXT_CS0 != 0) ? WIUS_SPI_CS_SW : WIUS_SPI_CS_HW,
    .cs_pin = WIUS_SPI_EXT_CS0,
    .cs_polarity = 1,
    .freq = WIUS_SPI_FREQ,
    .mode = 0,
    .width = 8,
};

uint8_t wifi_rx_buffer[TP_WIFI_RX_BUFFER_SIZE] = {0};

extern osEventFlagsId_t event_flags;
osThreadId_t wifi_receive_thread_id;
osThreadAttr_t wifi_rx_thread_attr = {
    .name = "TP wifi receive",
    .stack_size = TP_THREAD_STACK_WIFI,
    .priority = osPriorityLow,
};

// UDP socket over which communication happens
wius_udp_t tp_socket = {0};
char client_ip[16] = {0};
int client_port = 0;

// Buffer for storing acquired data
tp_buffer_t tp_buf;

// Variables for the command functions
bool enable_udp_replies = false;
uint16_t n_packs_to_read = 0;
uint16_t cb_pack_id = 0;

void _tp_thread_wifi_receive(void *argument);
// void _tp_thread_transmit(void *argument);
void _tp_int_handler(uint32_t flag);
sl_status_t _tp_transmit_packages(void);

sl_status_t tp_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    LOG_I("Initializing TinyProbe");

    // Initialize power manager
    status = wius_power_init();
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error initializing power manager: 0x%lx", status);
        return status;
    }
    status = wius_power_set(WIUS_POWER_MODE_HIGH);
    if (SL_STATUS_OK != status)
    {
        LOG_W("Error setting high power mode");
    }

    // Initialize SPI
    status = wius_spi_init(WIUS_SPI_INST_0, &spi_config);
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error initializing FPGA SPI: 0x%lx", status);
        return status;
    }

    delay_ms(1000);

    // Initialize GPIO
    wius_gpio_init();
    wius_gpio_config(reset_pin);
    wius_gpio_config(int_pin);

//    // EXPERIMENTAL: Enable pulldown on INT pin
//    status = sl_si91x_gpio_driver_select_pad_driver_disable_state(int_pin.port_pin.pin, GPIO_PULLDOWN);
//    if (SL_STATUS_OK != status)
//    {
//        LOG_E("Error initializing INT pin pulldown: 0x%lx", status);
//        return status;
//    }

    // Attach FPGA interrupt
    status = wius_gpio_attach_interrupt(int_pin, WIUS_GPIO_INT_RISING, _tp_int_handler);
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error initializing INT pin callback: 0x%lx", status);
        return status;
    }

    // Initialize low speed configuration interfaces
    tp_mux_init();
    tp_power_init();

    // Reset the FPGA
    wius_gpio_put(reset_pin, false);
    delay_ms(10);
    wius_gpio_put(reset_pin, true);

    // Wait some time for PLL to settle
    delay_ms(10);

    LOG_D("Reset FPGA");

    // Select internal SPI slave module of the FPGA
    tp_mux_select(TP_MUX_FPGA);
    delay_ms(10);

#if !TP_TEST_MODE
    // Initialize the FPGA
    status = tp_fpga_init();
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error configuring FPGA: 0x%lx", status);
        return status;
    }

    LOG_D("Configured FPGA");
#endif

    // Enable power domains for TX chip
    tp_power_on();

    LOG_D("Enabled power domains");

#if !TP_TEST_MODE
    // Reset AFE and TX chip by writing a value to the dedicated register
    CHECK_STATUS(tp_fpga_write_reg_safe(0x00000057, 10));
    // 10 ms delay
    delay_ms(10);
    // Remove reset signals and set TR_EN to 0
    CHECK_STATUS(tp_fpga_write_reg_safe(0x00000054, 10));

    // Turn on active control of the AFE clk (power downs in between shots)
    CHECK_STATUS(tp_fpga_write_reg_safe(0x4000ffff, 2));

    LOG_D("Reset AFE and TX");
#endif

    // Select TX
    tp_mux_select(TP_MUX_TX);
    delay_ms(10);

#if !TP_TEST_MODE
    // TX chip setup //
    // Config TX chip
    CHECK_STATUS(tp_tx_init());

    // Turn on also active control of the TX BF clk
    // (power downs in between TR_EN wake ups)
    // tp_fpga_write_reg_safe(0x0000ffff, 2);
    tp_fpga_write_reg_safe(0x0000ffff, 2); // TEST: Enable clocks by default (no waveform generator)

    LOG_D("Configured TX");
#endif

    // Switch the MUX to the AFE
    tp_mux_select(TP_MUX_AFE);
    delay_ms(10);

#if !TP_TEST_MODE
    // AFE setup //
    // Config AFE
    CHECK_STATUS(tp_afe_init());
    CHECK_STATUS(tp_afe_test_pattern(HALF_ZEROS_HALF_ONES));

    // Set AFE Gain
    CHECK_STATUS(tp_afe_write_reg_dtgc_safe(0xB5, 0));

    LOG_D("Configured AFE");
#endif

    // Select the internal SPI slave module of the FPGA
    tp_mux_select(TP_MUX_FPGA);
    delay_ms(10);

#if !TP_TEST_MODE
    //        // Enable AFE Fast Power down in between the shots
    //        // (controlled by waveform_gen)
    //        tp_fpga_write_reg_safe(0x00000050, 10);
    //        // Enable AFE Global Power down in between the shots
    //        // (controlled by waveform_gen)
    //        tp_fpga_write_reg_safe(0x00000044, 10);

    //            // Enable AFE Fast Power down and TR_EN signal duty cycling
    //            // AFE Global power down is manually disabled
    //            tp_fpga_write_reg_safe(0x00000010, 10);

    // Enable automatic AFE Fast Power down and TR_EN signal duty cycling
    // Enable AFE Global Power Down through pin
    tp_fpga_write_reg_safe(0x00000030, 10);
#endif

    // main_thread_id = osThreadNew(_tp_thread_main, NULL, &thread_attr);
    // if (main_thread_id == NULL)
    // {
    //   LOG_E("Error creating main thread");
    //   return SL_STATUS_FAIL;
    // }
    // LOG_D("Main thread started");

    LOG_I("Connecting to WiFi");
    // Connect to WiFi
    status = wius_wifi_init();
    while (SL_STATUS_OK != status)
    {
        LOG_W("Wi-Fi initialization failed with status 0x%lx, retrying in 1s...", status);
        wius_wifi_deinit();
        delay_ms(1000);
        status = wius_wifi_init();
    }
    LOG_I("Connected to WiFi");

    wifi_receive_thread_id = osThreadNew(_tp_thread_wifi_receive, NULL, &wifi_rx_thread_attr);
    if (wifi_receive_thread_id == NULL)
    {
        LOG_E("Error creating WiFi receive thread");
        return SL_STATUS_FAIL;
    }
    LOG_D("Wifi thread started");

//    CHECK_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_LOWPOWER));
//    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_LOW));
//    LOG_D("Low power mode activated");

    LOG_I("TinyProbe initialized");

    return status;
}

void tp_main_thread(void)
{
    sl_status_t status = SL_STATUS_OK;

//    LOG_D("Started TinyProbe main thread");

    common_init();

    LOG_I("TinyProbe ready");

    while (true)
    {
        // Wait for a command to be received
        if (!(osEventFlagsWait(event_flags, FLAG_CMD_RECEIVED, 0, 1000) & FLAG_CMD_RECEIVED))
        {
            LOG_I("Still here");
            continue;
        }

        // led_red_set(true);

        // Execute the command
        status = tp_command_parse_and_execute(wifi_rx_buffer, TP_WIFI_RX_BUFFER_SIZE);
        if (SL_STATUS_OK != status)
        {
            LOG_E("Error executing command: 0x%lx", status);
        }

        // Set the command executed flag
        osEventFlagsSet(event_flags, FLAG_CMD_EXECUTED);

        // led_red_set(false);
    }
}

void _tp_thread_wifi_receive(void *argument)
{
    // listens for incoming UDP packets
    (void)argument;
    sl_status_t status = SL_STATUS_OK;

//    LOG_D("Started TinyProbe WiFi receive thread");

    wius_udp_init(&tp_socket);

    status = wius_udp_bind(&tp_socket, 0, TP_UDP_PORT);
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error connecting UDP socket: 0x%lx", status);
        return;
    }

    ssize_t received_len = 0;

    while (true)
    {
        memset(wifi_rx_buffer, 0, TP_WIFI_RX_BUFFER_SIZE);

        status = wius_udp_receivefrom(&tp_socket, wifi_rx_buffer, TP_WIFI_RX_BUFFER_SIZE, &received_len,
                                      client_ip, sizeof(client_ip), &client_port, 0);
        if (SL_STATUS_OK != status)
        {
            LOG_E("Error receiving UDP packet: 0x%lx", status);
            continue;
        }

        LOG_I("Received UDP packet from %s:%d", client_ip, client_port);
        // LOG_D("Packet: '%s'", wifi_rx_buffer);

        // Parse the command
        if (tp_command_parse(wifi_rx_buffer, TP_WIFI_RX_BUFFER_SIZE) == NULL)
        {
            LOG_E("Invalid command, skipping");
            continue;
        }

        LOG_D("Valid command");

        // Set the command received flag
        osEventFlagsSet(event_flags, FLAG_CMD_RECEIVED);

        // Wait for the command to be executed
        if (!(osEventFlagsWait(event_flags, FLAG_CMD_EXECUTED, 0, 5000) & FLAG_CMD_EXECUTED))
        {
            LOG_W("Timeout waiting for command executed flag");
//            LOG_E("Error waiting for command executed flag");

            continue;
        }

        LOG_D("Stack space: %lu", osThreadGetStackSpace(wifi_receive_thread_id));
    }
}

sl_status_t tp_ping(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args;
    (void)args_length;

    sl_status_t status = SL_STATUS_OK;

    // TODO: Check implementation with Sergei
    char reply[32] = {0};
    snprintf(reply, sizeof(reply), "TinyProbe %d", TP_PROBE_ID);
    CHECK_STATUS(wius_udp_sendto(&tp_socket, (const uint8_t *)reply, strlen(reply), client_ip, client_port));

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_en_replies(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;

    // enable_udp_replies = *(bool *)args;
    enable_udp_replies = GET(args, uint8_t, 0) ? true : false;

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_sw_mux(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;

    // tp_mux_t mux = *(tp_mux_t *)args;
    // tp_mux_select(mux);
    tp_mux_t mux = GET(args, tp_mux_t, 0);
    tp_mux_select(mux);

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_write_spi(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args;
    (void)args_length;

    // TODO: Implement
    LOG_W("Not yet implemented");

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_write_fpga(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;
    sl_status_t status = SL_STATUS_OK;

    // uint8_t fpga_reg_addr = *args;
    // uint32_t fpga_reg_value = *(uint32_t *)(args + 1);
    uint8_t fpga_reg_addr = GET(args, uint8_t, 0);
    uint32_t fpga_reg_value = GET(args, uint32_t, 1);

    LOG_D("Writing %lu to %u", fpga_reg_value, fpga_reg_addr);

    CHECK_STATUS(tp_fpga_write_reg_safe(fpga_reg_value, fpga_reg_addr));

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_write_afe(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;
    sl_status_t status = SL_STATUS_OK;

    // uint8_t dtgc_reg_flag = *args;
    // uint8_t afe_reg_addr = *(args + 1);
    // uint16_t afe_reg_value = *(uint16_t *)(args + 2);
    uint8_t dtgc_reg_flag = GET(args, uint8_t, 0);
    uint8_t afe_reg_addr = GET(args, uint8_t, 1);
    uint16_t afe_reg_value = GET(args, uint16_t, 2);

    if (dtgc_reg_flag)
    {
        CHECK_STATUS(tp_afe_write_reg_dtgc(afe_reg_addr, afe_reg_value));
    }
    else
    {
        CHECK_STATUS(tp_afe_write_reg(afe_reg_addr, afe_reg_value));
    }

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_write_tx(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;
    sl_status_t status = SL_STATUS_OK;

    // uint16_t tx_reg_addr = *(uint16_t *)args;
    // uint32_t tx_reg_value = *(uint32_t *)(args + 2);
    uint16_t tx_reg_addr = GET(args, uint16_t, 0);
    uint32_t tx_reg_value = GET(args, uint32_t, 2);

    CHECK_STATUS(tp_tx_write_reg(tx_reg_addr, tx_reg_value));

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_delay_ns(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;

    // uint32_t delay = *(uint32_t *)args;
    uint64_t delay = GET(args, uint64_t, 0);
    delay_ns(delay);

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_sleep_ms(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;

    // uint32_t delay = *(uint32_t *)args;
    uint32_t delay = GET(args, uint32_t, 0);
    delay_ms(delay);

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t tp_ctrl_pwr(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;

    // tp_power_domain_t domain = *(tp_power_domain_t *)args;
    // bool enabled = *(bool *)(args + 1);
    tp_power_domain_t domain = GET(args, tp_power_domain_t, 0);
    uint8_t enabled = GET(args, uint8_t, 1);
    tp_power_set(domain, enabled ? true : false);

    LOG_D("Done");

    return SL_STATUS_OK;
}

volatile bool fpga_ready = false;

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

    LOG_I("Triggering %lu shots with %u packets to read", n_shots, n_packs_to_read);
    LOG_I("%u packets with %u packets concatenated", (n_packs_to_read + (TP_UDP_PACKET_AMT - 1)) / TP_UDP_PACKET_AMT, TP_UDP_PACKET_AMT);

//    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_HIGH));
//    CHECK_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_HIGHSPEED));
//    LOG_D("High speed mode activated");

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
//        if (!(osEventFlagsWait(event_flags, FLAG_FIFO_DATA_READY, 0, osWaitForever)))
//        {
//            LOG_E("Error waiting for FIFO data ready flag");
//            continue;
//        }
        while (interrupt_count < 1)
        {
            // wait
        }
        interrupt_count -= 1;

        LOG_D("Interrupt received");
#else
        // delay_ms(1);
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

        if(cb_pack_id != 65535)
        {
            // Enable AFE Global power down
            tp_fpga_write_reg_safe(48, 10);
            // Disable LVDS IO bank of the FPGA
            tp_power_set(TP_POWER_DOMAIN_LVDS_2_5V, false);
        }

        tp_fpga_en_read();


        delay_ns(2400);

        _tp_transmit_packages();

        LOG_D("Transmitted");

        CHECK_STATUS(tp_fpga_reset_multififo());
    }

//    CHECK_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_LOWPOWER));
//    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_LOW));
//    LOG_D("Low power mode activated");

    LOG_D("Done");

    return SL_STATUS_OK;
}

sl_status_t _tp_transmit_packages(void)
{
    sl_status_t status = SL_STATUS_OK;

    LOG_D("Executing");

    tp_buffer_init(&tp_buf);

    tp_buffer_slot_t *slot_spi = tp_buffer_claim_writing(&tp_buf);
    if (NULL == slot_spi)
    {
        LOG_W("Timeout claiming initial buffer for write");
        return SL_STATUS_FAIL;
    }

    uint8_t tx_dummy[TP_BUFFER_SIZE] = {0};
    status = tp_fpga_read_fifo(tx_dummy, slot_spi->data, TP_BUFFER_SIZE, false);
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error starting initial SPI recv: 0x%04X", (unsigned)status);
        return status;
    }

    uint16_t n_packs_to_read_div = (n_packs_to_read + (TP_UDP_PACKET_AMT - 1)) / TP_UDP_PACKET_AMT;

    for (uint16_t i = 0; i < n_packs_to_read_div; i++)
    {
        // CHECK_STATUS(sl_si91x_power_manager_set_clock_scaling(SL_SI91X_POWER_MANAGER_POWERSAVE));
        CHECK_STATUS(wius_spi_await(WIUS_SPI_INST_0));
        // CHECK_STATUS(sl_si91x_power_manager_set_clock_scaling(SL_SI91X_POWER_MANAGER_PERFORMANCE));

        slot_spi->length = TP_BUFFER_SIZE;

        tp_buffer_return(&tp_buf, slot_spi, false);

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

            status = tp_fpga_read_fifo(tx_dummy, slot_spi->data, TP_BUFFER_SIZE, false);
            if (SL_STATUS_OK != status)
            {
                LOG_E("Error starting SPI recv: 0x%04X", (unsigned)status);
                return status;
            }
        }

        tp_buffer_slot_t *slot_udp = tp_buffer_claim_reading(&tp_buf);
        if (NULL == slot_udp)
        {
            LOG_E("Error claiming buffer for read");
            return SL_STATUS_FAIL;
        }

        // Prepend the packet with the shot number
        memcpy(slot_udp->data, &i, 2);

        status = wius_udp_sendto(&tp_socket, slot_udp->data, TP_BUFFER_SIZE, client_ip, client_port);
        if (SL_STATUS_OK != status)
            LOG_W("Error transmitting packet");

        tp_buffer_return(&tp_buf, slot_udp, true);
    }

    LOG_D("Done");

    return status;
}

// sl_status_t _tp_transmit_packages(void)
//{
//   sl_status_t status = SL_STATUS_OK;
//
//   uint8_t tx_buf[TP_UDP_PACKET_SIZE + 2] = {0};
//   tx_buf[0] = SP_RD_FIFO;
//   tx_buf[1] = SPI_DUMMY_ADDR;
//
//   for (uint16_t i = 0; i < n_packs_to_read; i++)
//   {
//     status = wius_udp_sendto(&tp_socket, tx_buf, TP_UDP_PACKET_SIZE + 2, client_ip, client_port);
//     if (SL_STATUS_OK != status)
//       LOG_W("Error transmitting packet");
//     delay_ns(149000);
////    delay_ms(2);
//  }
//
//  return status;
//}

void _tp_int_handler(uint32_t flag)
{
    UNUSED(flag);

//    osEventFlagsSet(event_flags, FLAG_FIFO_DATA_READY);
    interrupt_count += 1;
}
