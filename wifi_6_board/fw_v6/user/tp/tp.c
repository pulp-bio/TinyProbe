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
#include "cmsis_os2.h"

#include "tp_command.h"
#include "tp_mux.h"
#include "tp_fpga.h"
#include "tp_afe.h"
#include "tp_tx.h"
#include "tp_power.h"
#include "wius_power.h"
#include "wius_wifi.h"
#include "wius_spi.h"
#include "wius_tcp.h"
#include "wius_gpio.h"

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
osThreadId_t wifi_transmit_thread_id;
osThreadAttr_t wifi_tx_thread_attr = {
    .name = "TP wifi transmit",
    .stack_size = TP_THREAD_STACK_WIFI,
    .priority = osPriorityNormal,
};

wius_wifi_mdns_t tp_mdns = {
    .host_name = "wius",
    .service_name = "tinyprobe",
    .service_message = "TinyProbe Service",
    .protocol = "udp",
    .port = TP_UDP_PORT,
};

// Synchronization variables
osSemaphoreId_t sem_fpga;

// Buffer for storing acquired data
tp_buffer_t tp_buf;

// Last server message
wius_tcp_server_message_t msg;

// Variables for the command functions
bool enable_udp_replies = false;
uint16_t n_packs_to_read = 0;
uint16_t cb_pack_id = 0;

uint32_t transmit_times[256] = {0};
size_t transmit_times_index = 0;

void _tp_thread_wifi_transmit(void *argument);
void _tp_int_handler(uint32_t flag);

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

    //    delay_ms(1000);

    // Initialize GPIO
    wius_gpio_init();
    wius_gpio_config(reset_pin);
    wius_gpio_config(int_pin);

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

    sem_fpga = osSemaphoreNew(10, 0, NULL);
    if (sem_fpga == NULL)
    {
        LOG_E("Error creating FPGA semaphore");
        return SL_STATUS_FAIL;
    }

    CHECK_STATUS(tp_buffer_init(&tp_buf));

    wifi_transmit_thread_id = osThreadNew(_tp_thread_wifi_transmit, NULL, &wifi_tx_thread_attr);
    if (wifi_transmit_thread_id == NULL)
    {
        LOG_E("Error creating WiFi transmit thread");
        return SL_STATUS_FAIL;
    }
    LOG_D("Wifi threads started");

    CHECK_STATUS(wius_wifi_mdns_init(&tp_mdns));
    CHECK_STATUS(wius_wifi_mdns_add(&tp_mdns));

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

    status = wius_tcp_server_init();
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error initializing TCP server: 0x%lx", status);
        return;
    }

    status = wius_tcp_server_start(TP_TCP_PORT);
    if (SL_STATUS_OK != status)
    {
        LOG_E("Error starting TCP server: 0x%lx", status);
        return;
    }
    LOG_I("Waiting for TCP connections on port %d", TP_TCP_PORT);

    tp_buffer_history_reset();

    LOG_I("TinyProbe ready");

    while (true)
    {
        tp_buffer_history_reset();

        osStatus_t os_status = osMessageQueueGet(wius_tcp_server_queue, &msg, NULL, 2000);
        if (os_status != osOK)
        {
            if (os_status == osErrorTimeout)
            {
                // Timeout, continue to next iteration
                LOG_I("Still here...");
                continue;
            }

            LOG_W("Error receiving TCP message from queue: %d", (int)os_status);
            continue;
        }

        status = tp_command_parse_and_execute(msg.data, msg.length, &msg);
        if (SL_STATUS_OK != status)
        {
            LOG_W("Error executing command: 0x%lx", status);
            continue;
        }

        // led_red_set(false);
        uint32_t stack_watermark = osThreadGetStackSpace(osThreadGetId());
        LOG_I("Main thread stack watermark: %lu bytes", stack_watermark);
        stack_watermark = osThreadGetStackSpace(wifi_transmit_thread_id);
        LOG_I("WiFi transmit thread stack watermark: %lu bytes", stack_watermark);

        // uint32_t *buffer_history;
        // size_t history_length = tp_buffer_history_get(&buffer_history);
        // LOG_I("Buffer history (length %d):", (int)history_length);
        // for (size_t i = 0; i < history_length; i++)
        // {
        //     uint32_t entry = buffer_history[i];
        //     uint32_t timestamp = entry & 0xFFFF;
        //     uint32_t event = (entry >> 24) & 0xFF;
        //     uint32_t buffer_index = (entry >> 16) & 0xFF;

        //     LOG_I("  %5d,%d,%d", timestamp, event, buffer_index);
        // }
    }
}

void _tp_thread_wifi_transmit(void *argument)
{
    // listens for incoming UDP packets
    (void)argument;
    sl_status_t status = SL_STATUS_OK;

    // LOG_D("Started TinyProbe WiFi transmit thread");

    while (1)
    {
        tp_buffer_slot_t *slot_udp = tp_buffer_claim_reading(&tp_buf);
        if (NULL == slot_udp)
        {
            LOG_E("Error claiming buffer for read");
            continue;
        }

        transmit_times[transmit_times_index++] = DWT->CYCCNT;
        if (transmit_times_index >= 256)
        {
            transmit_times_index = 0;
        }

        //        LOG_I("Transmitting UDP packet of length %d to %s:%d", TP_BUFFER_SIZE, client_ip, client_port);

        status = wius_tcp_server_respond_udp(&msg, TP_UDP_PORT, slot_udp->data, TP_BUFFER_SIZE);
        if (SL_STATUS_OK != status)
        {
            LOG_W("Error transmitting UDP packet: 0x%lx", status);
        }

        tp_buffer_return_reading(&tp_buf, slot_udp);

        // uint32_t stack_watermark = osThreadGetStackSpace(osThreadGetId());
        // LOG_I("WiFi transmit thread stack watermark: %lu bytes", stack_watermark);
    }
}

volatile uint32_t count_interrupt = 0;

void _tp_int_handler(uint32_t flag)
{
    UNUSED(flag);

    count_interrupt = DWT->CYCCNT;

    osSemaphoreRelease(sem_fpga);
}

// OS stack overflow hook
void vApplicationStackOverflowHook(void *xTask, char *pcTaskName)
{
    UNUSED(xTask);

    LOG_E("Stack overflow in task %s", pcTaskName);
    while (1)
        ;
}