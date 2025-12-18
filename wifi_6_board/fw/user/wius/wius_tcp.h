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

//! Maximum number of TCP server clients
#ifndef WIUS_TCP_SERVER_MAX_CLIENTS
#define WIUS_TCP_SERVER_MAX_CLIENTS 5
#endif
//! TCP server message queue size
#ifndef WIUS_TCP_SERVER_QUEUE_SIZE
#define WIUS_TCP_SERVER_QUEUE_SIZE 10
#endif
//! TCP server message data size
#ifndef WIUS_TCP_SERVER_MESSAGE_DATA_SIZE
#define WIUS_TCP_SERVER_MESSAGE_DATA_SIZE 1000
#endif

/**
 * @brief TCP connection message structure
 *
 */
typedef struct wius_tcp_server_message
{
    int socket;                                      /**< Client socket */
    uint8_t data[WIUS_TCP_SERVER_MESSAGE_DATA_SIZE]; /**< Body data */
    size_t length;                                   /**< Length of the body data */
    const sl_si91x_socket_metadata_t *meta;          /**< Metadata associated with the message */
} wius_tcp_server_message_t;

extern osMessageQueueId_t wius_tcp_server_queue; /**< TCP server message queue identifier */

/**
 * @brief Initialize the TCP server
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_ALLOCATION_FAILED: Memory allocation failed
 *
 * @note This function must be called before any other TCP function
 *
 */
sl_status_t wius_tcp_server_init(void);

/**
 * @brief Deinitialize the TCP server
 *
 * @retval SL_STATUS_OK: Success
 *
 */
sl_status_t wius_tcp_server_deinit(void);

/**
 * @brief Start the TCP server on the specified port
 *
 * @param port: Port number to listen on
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Failure (During socket creation, binding or listening)
 *
 * @note The server must be initialized with @ref wius_tcp_server_init before starting
 * @note The exact cause of failure can be found by reading the errno variable
 *
 */
sl_status_t wius_tcp_server_start(uint16_t port);

/**
 * @brief Stop the TCP server
 *
 * @retval SL_STATUS_OK: Success
 *
 */
sl_status_t wius_tcp_server_stop(void);

/**
 * @brief Send a response to a TCP client
 *
 * @param msg: Pointer to the message structure containing client info
 * @param response: Pointer to the response data
 * @param response_length: Length of the response data
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Failure (During sending)
 *
 * @note The server must be started with @ref wius_tcp_server_start before sending responses
 * @note The exact cause of failure can be found by reading the errno variable
 * @note The msg parameter only has to contain the client socket
 *
 */
sl_status_t wius_tcp_server_respond(wius_tcp_server_message_t *msg, char *response, size_t response_length);

/**
 * @brief Send a UDP response to a specified IP and port
 *
 * @param msg: Pointer to the message structure containing client info
 * @param port: Destination port number
 * @param response: Pointer to the response data
 * @param response_length: Length of the response data
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Failure (During socket creation or sending)
 *
 * @note The server must be started with @ref wius_tcp_server_start before sending responses
 * @note The exact cause of failure can be found by reading the errno variable
 * @note The msg parameter only has to contain the destination IP address in its metadata
 *
 */
sl_status_t wius_tcp_server_respond_udp(wius_tcp_server_message_t *msg, uint16_t port, uint8_t *response, size_t response_length);

/**
 * @brief Send an "OK" response to a TCP client
 *
 * @param msg: Pointer to the message structure containing client info
 * @param cmd_id: Command identifier
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Failure (During sending)
 *
 * @note The msg parameter only has to contain the client socket
 *
 */
sl_status_t wius_tcp_server_respond_ok(wius_tcp_server_message_t *msg, uint8_t cmd_id);

/**
 * @brief Send an "Error" response to a TCP client
 *
 * @param msg: Pointer to the message structure containing client info
 * @param cmd_id: Command identifier
 * @param error_code: Error code to send
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Failure (During sending)
 *
 * @note The msg parameter only has to contain the client socket
 *
 */
sl_status_t wius_tcp_server_respond_error(wius_tcp_server_message_t *msg, uint8_t cmd_id, sl_status_t error_code);

/**
 * @brief Send data to a TCP client
 *
 * @param msg: Pointer to the message structure containing client info
 * @param cmd_id: Command identifier
 * @param data: Pointer to the data to send
 * @param data_length: Length of the data to send
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_TRANSMIT: Failure during transmission
 * @retval SL_STATUS_TRANSMIT_INCOMPLETE: Incomplete transmission
 *
 * @note The msg parameter only has to contain the client socket
 *
 */
sl_status_t wius_tcp_server_respond_data(wius_tcp_server_message_t *msg, uint8_t cmd_id, uint8_t *data, size_t data_length);
