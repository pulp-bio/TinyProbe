/**
 * @file wius_tcp.h
 *
 * @brief WiUS TCP implementation header file
 *
 * @date 17.12.2025
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

#pragma once

#include "common.h"

#include "sl_si91x_socket.h"

#define WIUS_TCP_SERVER_MAX_CLIENTS 5
#define WIUS_TCP_SERVER_QUEUE_SIZE 10
#define WIUS_TCP_SERVER_MESSAGE_DATA_SIZE 1000

typedef struct wius_tcp_server_message
{
    int socket;
    uint8_t data[WIUS_TCP_SERVER_MESSAGE_DATA_SIZE];
    size_t length;
    const sl_si91x_socket_metadata_t *meta;
} wius_tcp_server_message_t;

extern osMessageQueueId_t wius_tcp_server_queue;

sl_status_t wius_tcp_server_init(void);
sl_status_t wius_tcp_server_deinit(void);

sl_status_t wius_tcp_server_start(uint16_t port);
sl_status_t wius_tcp_server_stop(void);

sl_status_t wius_tcp_server_respond(wius_tcp_server_message_t *msg, char *response, size_t response_length);
sl_status_t wius_tcp_server_respond_udp(wius_tcp_server_message_t *msg, uint16_t port, uint8_t *response, size_t response_length);

sl_status_t wius_tcp_server_respond_ok(wius_tcp_server_message_t *msg, uint8_t cmd_id);
sl_status_t wius_tcp_server_respond_error(wius_tcp_server_message_t *msg, uint8_t cmd_id, sl_status_t error_code);
sl_status_t wius_tcp_server_respond_data(wius_tcp_server_message_t *msg, uint8_t cmd_id, uint8_t *data, size_t data_length);
