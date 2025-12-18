/**
 * @file wius_tcp.c
 *
 * @brief WiUS TCP implementation source file
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

#include "wius_tcp.h"

#include <stdlib.h>
#include <string.h>

#include "errno.h"
#include "netinet_in.h"
#include "socket.h"
#include "sl_si91x_core_utilities.h"
#include "sl_si91x_socket_constants.h"

int sock;                                      /**< TCP server socket */
int client_socks[WIUS_TCP_SERVER_MAX_CLIENTS]; /**< Array of client sockets */
int udp_sock;                                  /**< UDP socket for UDP responses */
struct sockaddr_in server_addr;                /**< Server address structure */
osMessageQueueId_t wius_tcp_server_queue;      /**< TCP server message queue identifier */

/**
 * @brief Add a new client socket to the list
 *
 * @param socket: Client socket to add
 *
 * @return int: Index of the added socket, -1 if no space available
 *
 */
static int _wius_tcp_server_add_client(int socket)
{
    for (size_t i = 0; i < WIUS_TCP_SERVER_MAX_CLIENTS; i++)
    {
        if (client_socks[i] == -1)
        {
            client_socks[i] = socket;
            return i;
        }
    }
    sl_si91x_shutdown(socket, 0);
    return -1; // No space available
}

/**
 * @brief Remove a client socket from the list
 *
 * @param socket: Client socket to remove
 *
 * @return int: Index of the removed socket, -1 if not found
 *
 */
static int _wius_tcp_server_remove_client(int socket)
{
    for (size_t i = 0; i < WIUS_TCP_SERVER_MAX_CLIENTS; i++)
    {
        if (client_socks[i] == socket)
        {
            client_socks[i] = -1;
            sl_si91x_shutdown(socket, 0);
            return i;
        }
    }
    return -1; // Socket not found
}

/**
 * @brief Callback for remote termination of a socket
 *
 * @param socket: Socket that was terminated
 * @param port: Port number (unused)
 * @param bytes_sent: Bytes sent before termination (unused)
 *
 */
void _wius_tcp_server_cb_term(int socket, uint16_t port, uint32_t bytes_sent)
{
    UNUSED_PARAMETER(port);
    UNUSED_PARAMETER(bytes_sent);

    // When disconnected, remove the client socket from the list
    if (_wius_tcp_server_remove_client(socket) < 0)
    {
        LOG_E("Terminated socket %d not found", socket);
    }
}

/**
 * @brief Callback for receiving data on the TCP server socket
 *
 * @param socket: Socket on which data was received
 * @param buffer: Buffer containing the received data
 * @param length: Length of the received data
 * @param meta: Metadata associated with the message
 *
 */
static void _wius_tcp_server_cb_rx(uint32_t socket, uint8_t *buffer, uint32_t length, const sl_si91x_socket_metadata_t *meta)
{
    UNUSED_PARAMETER(meta);

    // Parse and enqueue the received message
    wius_tcp_server_message_t msg;
    msg.socket = socket;
    msg.length = (length < WIUS_TCP_SERVER_MESSAGE_DATA_SIZE) ? length : WIUS_TCP_SERVER_MESSAGE_DATA_SIZE;
    memcpy(msg.data, buffer, msg.length);
    msg.meta = meta;

    LOG_D("Received data of length %d on socket %ld\r\n", msg.length, socket);

    if (osMessageQueuePut(wius_tcp_server_queue, &msg, 0, 0) != osOK)
    {
        LOG_W("Failed to send message to queue");
    }
}

/**
 * @brief Callback for accepting a new client connection
 *
 * @param socket: New client socket
 * @param addr: Address of the client
 * @param ip_version: IP version of the client
 *
 */
static void _wius_tcp_server_cb_accept(int32_t socket, struct sockaddr *addr, uint8_t ip_version)
{
    UNUSED_PARAMETER(addr);
    UNUSED_PARAMETER(ip_version);

    LOG_D("INF: Accepted connection on socket %ld\r\n", socket);

    // Add the new client socket to the list
    if (_wius_tcp_server_add_client(socket) < 0)
    {
        LOG_E("No space for new client socket %ld, closing", socket);
    }

    // Continue accepting new connections, otherwise we only ever accept one
    if (sl_si91x_accept_async(sock, _wius_tcp_server_cb_accept) < 0)
    {
        LOG_E("Accept failed: %s", strerror(errno));
        sl_si91x_shutdown(sock, 0);
    }
}

sl_status_t wius_tcp_server_init(void)
{
    sock = -1;
    udp_sock = -1;

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;

    memset(client_socks, -1, sizeof(int) * WIUS_TCP_SERVER_MAX_CLIENTS);

    wius_tcp_server_queue = osMessageQueueNew(WIUS_TCP_SERVER_QUEUE_SIZE, sizeof(wius_tcp_server_message_t), NULL);
    if (wius_tcp_server_queue == NULL)
    {
        wius_tcp_server_deinit();
        return SL_STATUS_ALLOCATION_FAILED;
    }

    sl_si91x_set_remote_termination_callback(_wius_tcp_server_cb_term);

    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_deinit(void)
{
    if (sock >= 0)
    {
        sl_si91x_shutdown(sock, 0);
    }
    if (udp_sock >= 0)
    {
        sl_si91x_shutdown(udp_sock, 0);
    }
    sock = -1;
    udp_sock = -1;

    osMessageQueueDelete(wius_tcp_server_queue);

    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_start(uint16_t port)
{
    sock = sl_si91x_socket_async(AF_INET, SOCK_STREAM, IPPROTO_TCP, _wius_tcp_server_cb_rx);
    if (sock < 0)
    {
        LOG_E("Socket creation failed: %s", strerror(errno));
        return SL_STATUS_FAIL;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = 0; // Bind to all interfaces
    server_addr.sin_port = htons(port);
    if (sl_si91x_bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        LOG_E("Bind failed: %s", strerror(errno));
        sl_si91x_shutdown(sock, 0);
        return SL_STATUS_FAIL;
    }

    if (sl_si91x_listen(sock, WIUS_TCP_SERVER_MAX_CLIENTS) < 0)
    {
        LOG_E("Listen failed: %s", strerror(errno));
        sl_si91x_shutdown(sock, 0);
        return SL_STATUS_FAIL;
    }

    if (sl_si91x_accept_async(sock, _wius_tcp_server_cb_accept) < 0)
    {
        LOG_E("Accept failed: %s", strerror(errno));
        sl_si91x_shutdown(sock, 0);
        return SL_STATUS_FAIL;
    }

    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_stop(void)
{
    if (sock >= 0)
    {
        sl_si91x_shutdown(sock, 0);
        sock = -1;
    }
    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_respond(wius_tcp_server_message_t *msg, char *response, size_t response_length)
{
    if (sl_si91x_send_async(msg->socket, (uint8_t *)response, response_length, 0, NULL) < 0)
    {
        LOG_E("Error sending response on socket %d: %s", msg->socket, strerror(errno));
        return SL_STATUS_FAIL;
    }
    return SL_STATUS_OK;
}

/**
 * @brief Callback for receiving data on the UDP socket
 *
 * @param socket: Socket on which data was received
 * @param buffer: Buffer containing the received data
 * @param length: Length of the received data
 * @param firmware_socket_response: Metadata associated with the message
 *
 * @warning This callback will not process any received data, as the UDP socket is only used for sending responses
 *
 */
static void _wius_tcp_server_cb_udp_rx(uint32_t socket,
                                       uint8_t *buffer,
                                       uint32_t length,
                                       const sl_si91x_socket_metadata_t *firmware_socket_response)
{
    UNUSED_PARAMETER(buffer);
    UNUSED_PARAMETER(length);
    UNUSED_PARAMETER(firmware_socket_response);

    LOG_W("Unexpected data received on socket %lu", socket);
}

/**
 * @brief Callback for UDP send completion
 *
 * @param socket: Socket on which data was sent
 * @param length: Length of the sent data
 *
 * @warning This callback is actually never called but necessary for async sendto
 *
 */
void _wius_tcp_server_respond_udp_done_handler(int32_t socket, uint16_t length)
{
    UNUSED_PARAMETER(socket);
    UNUSED_PARAMETER(length);

    LOG_D("Transmit on socket %d of length %u done", socket, length);
}

sl_status_t wius_tcp_server_respond_udp(wius_tcp_server_message_t *msg, uint16_t port, uint8_t *response, size_t response_length)
{
    UNUSED_PARAMETER(response);

    if (udp_sock < 0)
    {
        udp_sock = sl_si91x_socket_async(AF_INET, SOCK_DGRAM, IPPROTO_UDP, _wius_tcp_server_cb_udp_rx);
        // udp_sock = sl_si91x_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (udp_sock < 0)
        {
            LOG_E("Error creating UDP socket");
            return SL_STATUS_FAIL;
        }

        // This socket is only used for sending, so set high performance option which can improve throughput
        uint32_t option = SLI_SI91X_HIGH_PERFORMANCE_SOCKET;
        if (sl_si91x_setsockopt(udp_sock, SOL_SOCKET, SL_SI91X_SO_HIGH_PERFORMANCE_SOCKET, &option, sizeof(option)) < 0)
        {
            LOG_E("Error setting socket options");
            sl_si91x_shutdown(udp_sock, 0);
            udp_sock = -1;
            return SL_STATUS_FAIL;
        }

        LOG_I("Created UDP socket %d for %u.%u.%u.%u:%u", udp_sock, msg->meta->dest_ip_addr.ipv4_address[0],
              msg->meta->dest_ip_addr.ipv4_address[1], msg->meta->dest_ip_addr.ipv4_address[2],
              msg->meta->dest_ip_addr.ipv4_address[3], port);
    }

    // Copy destination address
    server_addr.sin_addr.s_addr = msg->meta->dest_ip_addr.ipv4_address[0] |
                                  (msg->meta->dest_ip_addr.ipv4_address[1] << 8) |
                                  (msg->meta->dest_ip_addr.ipv4_address[2] << 16) |
                                  (msg->meta->dest_ip_addr.ipv4_address[3] << 24);
    server_addr.sin_port = htons(port);

    // Send data in chunks of max 1400 bytes to respect MTU
    size_t total_sent = 0;
    while (total_sent < response_length)
    {
        size_t chunk_size = (response_length - total_sent > 1400) ? 1400 : (response_length - total_sent);

        int sent = sl_si91x_sendto_async(udp_sock,
                                         (uint8_t *)response + total_sent, chunk_size,
                                         0, (struct sockaddr *)&server_addr, sizeof(server_addr), _wius_tcp_server_respond_udp_done_handler);
        // int sent = sl_si91x_sendto(udp_sock, (uint8_t *)response + total_sent, chunk_size, 0, (struct sockaddr *)&server_addr, sizeof(server_addr));
        if (sent < 0)
        {
            LOG_E("Sendto failed: %s", strerror(errno));
            return SL_STATUS_FAIL;
        }

        total_sent += sent;
    }
    LOG_D("Sent UDP packet of size %d", response_length);

    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_respond_ok(wius_tcp_server_message_t *msg, uint8_t cmd_id)
{
    uint8_t response[3];
    response[0] = cmd_id;
    memcpy(&response[1], "OK", 2);
    return wius_tcp_server_respond(msg, (char *)response, sizeof(response));
}

sl_status_t wius_tcp_server_respond_error(wius_tcp_server_message_t *msg, uint8_t cmd_id, sl_status_t error_code)
{
    uint8_t response[3 + sizeof(sl_status_t)];
    response[0] = cmd_id;
    memcpy(&response[1], "ER", 2);
    memcpy(&response[3], &error_code, sizeof(sl_status_t));
    return wius_tcp_server_respond(msg, (char *)response, sizeof(response));
}

sl_status_t wius_tcp_server_respond_data(wius_tcp_server_message_t *msg, uint8_t cmd_id, uint8_t *data, size_t data_length)
{
    sl_status_t status = SL_STATUS_OK;

    UNUSED_PARAMETER(cmd_id);

    // // If we want to send another data response, we can do it here
    // size_t num_packets = (data_length + 1400) / 1400;
    // uint8_t response[4];
    // response[0] = cmd_id;
    // memcpy(&response[1], "DT", 2);
    // response[3] = (uint8_t)num_packets;
    // CHECK_STATUS(wius_tcp_server_respond(msg, (char *)response, sizeof(response)));

    // Here, we can use sl_si91x_send_large_data to send the data in chunks
    // This function handles splitting the data into MTU-sized packets internally but is not available for sendto
    int sent = sl_si91x_send_large_data(msg->socket, data, data_length, 0);
    if (sent < 0)
    {
        LOG_E("Send failed: %s", strerror(errno));
        return SL_STATUS_TRANSMIT;
    }
    if (sent != (int)data_length)
    {
        return SL_STATUS_TRANSMIT_INCOMPLETE;
    }

    return status;
}
