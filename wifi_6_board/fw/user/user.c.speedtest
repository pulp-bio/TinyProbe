/**
 * @file user.c
 *
 * @brief User main source file
 *
 * @date 08.09.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup common
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

#include "user.h"

#include <stdio.h>
#include "errno.h"

#include "common.h"
#include "wius_power.h"
#include "wius/wius_wifi.h"
#include "wius/wius_tcp.h"

static const uint8_t CLIENT_ADDR[4] = {192, 168, 50, 217};

#define BUFFER_SIZE 1400
#define TCP_PORT 2121
#define UDP_PORT 5000

uint8_t test_buffer[BUFFER_SIZE];

const osThreadAttr_t user_application_attr = {
    .name = "user_application",
    .priority = (osPriority_t)osPriorityNormal,
    .stack_size = TP_THREAD_STACK_MAIN,
};
osThreadId_t user_application_id;

void user_application(void *args);

static void rx_callback(uint32_t socket,
                        uint8_t *buffer,
                        uint32_t length,
                        const sl_si91x_socket_metadata_t *firmware_socket_response)
{
    UNUSED_PARAMETER(buffer);
    UNUSED_PARAMETER(length);
    UNUSED_PARAMETER(firmware_socket_response);

    LOG_W("Unexpected data received on socket %lu", socket);
}

sl_status_t user_loop()
{
    sl_status_t status = SL_STATUS_OK;

    CHECK_STATUS(wius_power_init());
    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_HIGH));

    LOG_I("Connecting Wi-Fi...");
    status = wius_wifi_init();
    while (SL_STATUS_OK != status)
    {
        LOG_W("Wi-Fi initialization failed with status 0x%lx, retrying in 1s...", status);
        wius_wifi_deinit();
        delay_ms(1000);
        status = wius_wifi_init();
    }
    // CHECK_STATUS(wius_wifi_set_performance_profile(WIUS_PERF_PROFILE_HIGHSPEED));
    LOG_I("Wi-Fi connected");

    // CHECK_STATUS(wius_tcp_server_init());
    // CHECK_STATUS(wius_tcp_server_start(TCP_PORT));
    // LOG_I("TCP server started on port %d", TCP_PORT);

    // wius_tcp_server_message_t msg;
    // while (osMessageQueueGet(wius_tcp_server_queue, &msg, NULL, 2000) != osOK)
    // {
    //     LOG_W("Error receiving initial TCP server message");
    // }

    // int sock = sl_si91x_socket_async(AF_INET, SOCK_DGRAM, IPPROTO_UDP, rx_callback);
    int sock = -1;
    while ((sock = sl_si91x_socket_async(AF_INET, SOCK_STREAM, IPPROTO_TCP, rx_callback)) < 0)
    {
        LOG_E("Error creating UDP socket: %s", strerror(errno));
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = (CLIENT_ADDR[0] << 0) |
                                  (CLIENT_ADDR[1] << 8) |
                                  (CLIENT_ADDR[2] << 16) |
                                  (CLIENT_ADDR[3] << 24);
    server_addr.sin_port = htons(UDP_PORT);

    while (sl_si91x_connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        LOG_E("Error connecting TCP socket: %s", strerror(errno));
    }

    LOG_I("TCP socket %d sending to %u.%u.%u.%u:%u", sock, CLIENT_ADDR[0],
          CLIENT_ADDR[1], CLIENT_ADDR[2], CLIENT_ADDR[3], UDP_PORT);

    LOG_I("Starting TCP send loop...");
    while (true)
    {
        // CHECK_STATUS(wius_tcp_server_respond_udp(&msg, UDP_PORT, test_buffer, BUFFER_SIZE));
        // int sent = sl_si91x_sendto_async(sock, test_buffer, BUFFER_SIZE, 0,
        //                                  (struct sockaddr *)&server_addr, sizeof(server_addr), NULL);
        int sent = sl_si91x_send_async(sock, test_buffer, BUFFER_SIZE, 0, NULL);
        if (sent < 0)
        {
            LOG_E("Sendto failed: %s", strerror(errno));
            return SL_STATUS_FAIL;
        }
        else if (sent != BUFFER_SIZE)
        {
            LOG_W("Partial send: %d / %d bytes", sent, BUFFER_SIZE);
        }
        // LOG_I("Sent %d bytes", sent);
        // osDelay(1);
        osThreadYield();
    }
}

void user_init(void)
{
    printf("--- Initializing user application ---\r\n");

    common_init();

    sl_status_t status = log_init();
    if (SL_STATUS_OK != status)
    {
        printf("!-- Failed to initialize log: 0x%04lx --!\r\n", status);
        return;
    }

    user_application_id = osThreadNew(user_application, NULL, &user_application_attr);
    if (user_application_id == NULL)
    {
        printf("!-- Failed to create user application thread --!\r\n");
        return;
    }

    printf("--- User application initialized ---\r\n");
}

void user_application(void *args)
{
    UNUSED(args);

    for (size_t i = 0; i < BUFFER_SIZE; i++)
    {
        test_buffer[i] = (uint8_t)('A' + i % 26);
    }

    LOG_I("Starting user loop...");
    sl_status_t status = user_loop();
    if (SL_STATUS_OK != status)
    {
        LOG_E("User loop failed: 0x%04lx", status);
    }
    LOG_W("User loop exited");
}
