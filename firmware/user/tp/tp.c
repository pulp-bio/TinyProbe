/**
 * @file tp.c
 *
 * @brief TinyProbe main source file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 *
 * @ingroup tinyprobe
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

#include <stdint.h>

#include "sl_si91x_power_manager.h"

#include "tp_methods.h"
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
    .cs_mode = WIUS_SPI_CS_SW,
    .cs_pin = WIUS_SPI_EXT_CS0,
    .cs_polarity = 0,
    .freq = WIUS_SPI_FREQ,
    .mode = 0,
    .width = 8,
};

uint8_t wifi_rx_buffer[TP_WIFI_RX_BUFFER_SIZE] = {0};

osThreadId_t wifi_transmit_thread_id;
osThreadAttr_t wifi_tx_thread_attr = {
    .name = "TP wifi transmit",
    .stack_size = TP_THREAD_STACK_WIFI,
    .priority = osPriorityBelowNormal1,
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

// Last server message and response buffer
wius_tcp_server_message_t msg;
char rsp_buffer[1024];     // Buffer to hold the framed protobuf response
size_t rsp_buffer_len = 0; // Length of the data in the rsp_buffer

void _tp_thread_wifi_transmit(void *argument);
void _tp_int_handler(uint32_t flag);
static void _tp_nanopb_sender(const char *response, size_t response_len);

sl_status_t tp_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    log_info("Initializing TinyProbe");

    // Initialize power manager
    status = wius_power_init();
    if (SL_STATUS_OK != status)
    {
        log_error("Error initializing power manager: 0x%lx", status);
        return status;
    }
    status = wius_power_set(WIUS_POWER_MODE_HIGH);
    if (SL_STATUS_OK != status)
    {
        log_warn("Error setting high power mode");
    }

    // Initialize SPI
    status = wius_spi_init(WIUS_SPI_INST_0, &spi_config);
    if (SL_STATUS_OK != status)
    {
        log_error("Error initializing FPGA SPI: 0x%lx", status);
        return status;
    }

    delay_ms(1000);

    // Initialize GPIO
    wius_gpio_init();
    wius_gpio_config(reset_pin);
    wius_gpio_config(int_pin);

    // Attach FPGA interrupt
    status = wius_gpio_attach_interrupt(int_pin, WIUS_GPIO_INT_RISING, _tp_int_handler);
    if (SL_STATUS_OK != status)
    {
        log_error("Error initializing INT pin callback: 0x%lx", status);
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

    log_debug("Reset FPGA");

    // Select internal SPI slave module of the FPGA
    tp_mux_select(TP_MUX_FPGA);
    delay_ms(10);

#if !TP_TEST_MODE
    // Initialize the FPGA
    status = tp_fpga_init();
    if (SL_STATUS_OK != status)
    {
        log_error("Error configuring FPGA: 0x%lx", status);
        return status;
    }

    log_debug("Configured FPGA");
#endif

    // Enable power domains for TX chip
    tp_power_on();

    log_debug("Enabled power domains");

#if !TP_TEST_MODE
    // Reset AFE and TX chip by writing a value to the dedicated register
    LOG_RET_STATUS(tp_fpga_write_reg_safe(0x00000057, 10));
    // 10 ms delay
    delay_ms(10);
    // Remove reset signals and set TR_EN to 0
    LOG_RET_STATUS(tp_fpga_write_reg_safe(0x00000054, 10));

    // Turn on active control of the AFE clk (power downs in between shots)
    LOG_RET_STATUS(tp_fpga_write_reg_safe(0x4000ffff, 2));

    log_debug("Reset AFE and TX");
#endif

    // Select TX
    tp_mux_select(TP_MUX_TX);
    delay_ms(10);

#if !TP_TEST_MODE
    // TX chip setup //
    // Config TX chip
    LOG_RET_STATUS(tp_tx_init());

    // Turn on also active control of the TX BF clk
    // (power downs in between TR_EN wake ups)
    // tp_fpga_write_reg_safe(0x0000ffff, 2);
    tp_fpga_write_reg_safe(0x0000ffff, 2); // TEST: Enable clocks by default (no waveform generator)

    log_debug("Configured TX");
#endif

    // Switch the MUX to the AFE
    tp_mux_select(TP_MUX_AFE);
    delay_ms(10);

#if !TP_TEST_MODE
    // AFE setup //
    // Config AFE
    LOG_RET_STATUS(tp_afe_init());
    LOG_RET_STATUS(tp_afe_test_pattern(HALF_ZEROS_HALF_ONES));

    // Set AFE Gain
    LOG_RET_STATUS(tp_afe_write_reg_dtgc_safe(0xB5, 0));

    log_debug("Configured AFE");
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

    log_info("Connecting to WiFi");
    // Connect to WiFi
    status = wius_wifi_init();
    while (SL_STATUS_OK != status)
    {
        log_warn("Wi-Fi initialization failed with status 0x%lx, retrying in 1s...", status);
        wius_wifi_deinit();
        delay_ms(1000);
        status = wius_wifi_init();
    }
    log_info("Connected to WiFi");

    sem_fpga = osSemaphoreNew(10, 0, NULL);
    if (sem_fpga == NULL)
    {
        log_error("Error creating FPGA semaphore");
        return SL_STATUS_FAIL;
    }

    LOG_RET_STATUS(tp_buffer_init(&tp_buf));

    wifi_transmit_thread_id = osThreadNew(_tp_thread_wifi_transmit, NULL, &wifi_tx_thread_attr);
    if (wifi_transmit_thread_id == NULL)
    {
        log_error("Error creating WiFi transmit thread");
        return SL_STATUS_FAIL;
    }
    log_debug("Wifi threads started");

    // LOG_RET_STATUS(wius_wifi_mdns_init(&tp_mdns));
    // LOG_RET_STATUS(wius_wifi_mdns_add(&tp_mdns));

    //    LOG_RET_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_LOWPOWER));
    //    LOG_RET_STATUS(wius_power_set(WIUS_POWER_MODE_LOW));
    //    log_debug("Low power mode activated");

    log_info("TinyProbe initialized");

    return status;
}

// #include <pb_encode.h>
// #include <pb_decode.h>
// #include "methods.pb.h"

wius_tcp_server_message_t payload = {0};
// methods_request req = methods_request_init_default;
// pb_istream_t istream;

sl_status_t tp_main_thread(void)
{
    sl_status_t status = SL_STATUS_OK;

    status = wius_tcp_server_init();
    if (SL_STATUS_OK != status)
    {
        log_error("Error initializing TCP server");
        LOG_STATUS(status);
        return status;
    }

    status = wius_tcp_server_start(TP_TCP_PORT);
    if (SL_STATUS_OK != status)
    {
        log_error("Error starting TCP server");
        LOG_STATUS(status);
        return status;
    }
    log_info("Waiting for TCP connections on port %d", TP_TCP_PORT);

    tp_buffer_history_reset();

    log_info("TinyProbe ready");
    log_info("Probe ID: %lu", TP_PROBE_ID);

    while (true)
    {
        tp_buffer_history_reset();

        osStatus_t os_status = osMessageQueueGet(wius_tcp_server_queue, &msg, NULL, 2000);
        if (os_status != osOK)
        {
            if (os_status == osErrorTimeout)
            {
                // Timeout, continue to next iteration
                log_info("Still here...");
                continue;
            }

            log_warn("Error receiving TCP message from queue: %d", (int)os_status);
            led_set(LED_COLOR_RED);
            continue;
        }
        led_set(LED_COLOR_YELLOW);

        // log_debug("Received TCP message of length %u bytes", (unsigned)msg.length);
        // We expect at least 4 bytes of length
        // - First 2 bytes are a magic number (0xAB0B) to identify valid messages
        // - Next 2 bytes are the data length (16-bit unsigned integer in big endian)
        if (msg.length < 4)
        {
            log_warn("Received message with invalid length");
            log_warn("Received length: %u", (unsigned)msg.length);
            log_warn("Expected minimum length: 4");
            led_set(LED_COLOR_RED);
            continue;
        }

        // Check bytes 0 and 1 for magic number 0xAB0B
        if (msg.data[0] != 0xAB || msg.data[1] != 0x0B)
        {
            log_warn("Received message with invalid magic bytes");
            log_warn("Received: 0x%02X 0x%02X", msg.data[0], msg.data[1]);
            log_warn("Expected: 0xAB 0x0B");
            led_set(LED_COLOR_RED);
            continue;
        }

        uint16_t data_length = ((uint16_t)msg.data[2] << 8) | msg.data[3];
        if (data_length != msg.length - 4)
        {
            log_warn("Received message with length mismatch");
            log_warn("Length in header: %u", data_length);
            log_warn("Actual length: %u", (unsigned)msg.length - 4);
            led_set(LED_COLOR_RED);
            continue;
        }

        // For handling, skip magic and length
        payload.socket = msg.socket;
        payload.length = msg.length - 4;
        payload.meta = msg.meta;
        memcpy(payload.data, msg.data + 4, payload.length);

        // log_trace("Decoding Protobuf request");
        // istream = pb_istream_from_buffer(payload.data, payload.length);
        // log_trace("Created istream for request data");
        // if (!pb_decode(&istream, methods_request_fields, &req))
        // {
        //     log_error("Failed to decode request: %s", istream.errmsg ? istream.errmsg : "unknown decode error");
        //     return SL_STATUS_FAIL;
        // }
        // log_debug("Decoded request with %u commands", (unsigned)req.cmd_count);

        // for (size_t i = 0; i < payload.length; i++)
        // {
        //     log_debug("- %2u: 0x%02X", (unsigned)i, payload.data[i]);
        // }

        // log_debug("Handling Protobuf request");
        tp_methods_handle(&payload, _tp_nanopb_sender);

        // log_info("Processed payload with %u bytes", (unsigned)payload.length);
        led_set(LED_COLOR_GREEN);
    }
}

void _tp_thread_wifi_transmit(void *argument)
{
    // listens for incoming UDP packets
    UNUSED(argument);
    sl_status_t status = SL_STATUS_OK;

    // log_debug("Started TinyProbe WiFi transmit thread");

    while (1)
    {
        tp_buffer_slot_t *slot_udp = tp_buffer_claim_reading(&tp_buf);
        if (NULL == slot_udp)
        {
            // log_error("Error claiming buffer for read");
            continue;
        }

        status = wius_tcp_server_respond_udp(&msg, TP_UDP_PORT, slot_udp->data, TP_BUFFER_SIZE);
        if (SL_STATUS_OK != status)
        {
            log_warn("Error transmitting UDP packet: 0x%lx", status);
        }
        // status = wius_tcp_server_respond_data(&msg, TP_CMD_TRIGGER_SHOT, slot_udp->data, TP_BUFFER_SIZE);
        // if (SL_STATUS_OK != status)
        // {
        //     log_warn("Error transmitting packet: 0x%lx", status);
        // }

        tp_buffer_return_reading(&tp_buf, slot_udp);

        // uint32_t stack_watermark = osThreadGetStackSpace(osThreadGetId());
        // log_info("WiFi transmit thread stack watermark: %lu bytes", stack_watermark);
    }
}

void _tp_int_handler(uint32_t flag)
{
    UNUSED(flag);

    osSemaphoreRelease(sem_fpga);
}

// OS stack overflow hook
void vApplicationStackOverflowHook(void *xTask, char *pcTaskName)
{
    UNUSED(xTask);

    log_error("Stack overflow in task %s", pcTaskName);
    while (1)
        ;
}

static void _tp_nanopb_sender(const char *response, size_t response_len)
{
    if (response_len > UINT16_MAX)
    {
        log_error("Response too large to frame: %u bytes", (unsigned)response_len);
        return;
    }

    if (response_len + 4 > sizeof(rsp_buffer))
    {
        log_error("TX buffer overflow, cannot send response");
        return;
    }

    rsp_buffer[0] = (char)0xAB;
    rsp_buffer[1] = (char)0x0B;
    rsp_buffer[2] = (char)((response_len >> 8) & 0xFF);
    rsp_buffer[3] = (char)(response_len & 0xFF);
    memcpy(rsp_buffer + 4, response, response_len);
    rsp_buffer_len = response_len + 4;

    if (wius_tcp_server_respond(&msg, rsp_buffer, rsp_buffer_len) != SL_STATUS_OK)
    {
        log_error("Could not send response to client");
    }

    rsp_buffer_len = 0;

    return;
}
