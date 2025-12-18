/**
 * @file wius_udp.h
 *
 * @brief WiUS UDP implementation header file
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

#include "socket.h"

#include "common.h"

/**
 * @brief UDP connection structure
 *
 * @note To be filled by @ref wius_udp_init
 *
 */
typedef struct wius_udp
{
    bool connected;                    /**< Connection status flag */
    int socket;                        /**< Socket file descriptor */
    struct sockaddr_in server_address; /**< Server address structure */
} wius_udp_t;

/**
 * @brief Initialize the UDP connection
 *
 * @param udp: UDP connection structure
 *
 * @note This function must be called before any other UDP function
 *
 */
void wius_udp_init(wius_udp_t *udp);

/**
 * @brief Bind the UDP socket
 *
 * @param udp: UDP connection structure
 * @param ip: Server IP address
 * @param port: Server port
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_SI91X_SOCKET_ALREADY_OPEN: Socket already binded
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CREATED: Socket creation failed
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CONNECTED: Socket binding failed
 *
 */
sl_status_t wius_udp_bind(wius_udp_t *udp, char *ip, int port);

/**
 * @brief Close the UDP socket
 *
 * @param udp: UDP connection structure
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CONNECTED: Socket not binded
 *
 */
sl_status_t wius_udp_close(wius_udp_t *udp);

/**
 * @brief Send data over a UDP connection
 *
 * @param udp: UDP connection structure
 * @param data: Data buffer
 * @param data_len: Data length
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CONNECTED: Socket not binded
 * @retval SL_STATUS_SI91X_IO_FAIL: Send failed
 *
 */
sl_status_t wius_udp_send(wius_udp_t *udp, const uint8_t *data, size_t data_len);

/**
 * @brief Send data over a UDP connection to a specific IP and port
 *
 * @param udp: UDP connection structure
 * @param data: Data buffer
 * @param data_len: Data length
 * @param ip: Destination IP address
 * @param port: Destination port
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CONNECTED: Socket not binded
 * @retval SL_STATUS_SI91X_IO_FAIL: Send failed
 *
 */
sl_status_t wius_udp_sendto(wius_udp_t *udp, const uint8_t *data, size_t data_len,
                            char *ip, int port);

/**
 * @brief Receive data over a UDP connection
 *
 * @param udp: UDP connection structure
 * @param buffer: Buffer to store received data
 * @param buffer_len: Buffer length
 * @param received_len: Pointer to store the received data length
 * @param timeout_ms: Timeout in milliseconds (set to <= 0 for blocking)
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CONNECTED: Socket not binded
 * @retval SL_STATUS_INVALID_PARAMETER: buffer or received_len is NULL
 * @retval SL_STATUS_SI91X_IO_FAIL: Receive failed
 *
 */
sl_status_t wius_udp_receive(wius_udp_t *udp, uint8_t *buffer, size_t buffer_len, ssize_t *received_len,
                             int32_t timeout_ms);

/**
 * @brief Receive data over a UDP connection and retrieve the sender IP and port
 *
 * @param udp: UDP connection structure
 * @param buffer: Buffer to store received data
 * @param buffer_len: Buffer length
 * @param received_len: Pointer to store the received data length
 * @param ip: Buffer to store the sender IP address (at least 16 bytes)
 * @param ip_len: IP buffer length (at least 16 bytes)
 * @param port: Pointer to store the sender port
 * @param timeout_ms: Timeout in milliseconds (set to <= 0 for blocking)
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_SI91X_SOCKET_NOT_CONNECTED: Socket not binded
 * @retval SL_STATUS_INVALID_PARAMETER: buffer or received_len is NULL
 * @retval SL_STATUS_SI91X_IO_FAIL: Receive failed
 *
 */
sl_status_t wius_udp_receivefrom(wius_udp_t *udp, uint8_t *buffer, size_t buffer_len, ssize_t *received_len,
                                 char *ip, size_t ip_len, int *port, int32_t timeout_ms);
