#include "wius_tcp.h"

#include <stdlib.h>
#include <string.h>

#include "errno.h"
#include "netinet_in.h"
#include "socket.h"
#include "sl_si91x_core_utilities.h"
#include "sl_si91x_socket_constants.h"

int sock;
int client_socks[WIUS_TCP_SERVER_MAX_CLIENTS];
int udp_sock;
struct sockaddr_in server_addr;
osMessageQueueId_t wius_tcp_server_queue;

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

void _wius_tcp_server_cb_term(int socket, uint16_t port, uint32_t bytes_sent)
{
    UNUSED_PARAMETER(port);
    UNUSED_PARAMETER(bytes_sent);

    if (_wius_tcp_server_remove_client(socket) < 0)
    {
        LOG_E("Terminated socket %d not found", socket);
    }
}

static void _wius_tcp_server_cb_rx(uint32_t socket, uint8_t *buffer, uint32_t length, const sl_si91x_socket_metadata_t *meta)
{
    UNUSED_PARAMETER(meta);

    wius_tcp_server_message_t msg;
    msg.socket = socket;
    msg.length = (length < WIUS_TCP_SERVER_MESSAGE_DATA_SIZE) ? length : WIUS_TCP_SERVER_MESSAGE_DATA_SIZE;
    memcpy(msg.data, buffer, msg.length);
    msg.meta = meta;

    // printf("INF: Received data of length %d on socket %ld\r\n", msg.length, socket);

    if (osMessageQueuePut(wius_tcp_server_queue, &msg, 0, 0) != osOK)
    {
        LOG_W("Failed to send message to queue");
    }
}

static void _wius_tcp_server_cb_accept(int32_t socket, struct sockaddr *addr, uint8_t ip_version)
{
    UNUSED_PARAMETER(addr);
    UNUSED_PARAMETER(ip_version);

    // printf("INF: Accepted connection on socket %ld\r\n", socket);

    if (_wius_tcp_server_add_client(socket) < 0)
    {
        LOG_E("No space for new client socket %ld, closing", socket);
    }

    if (sl_si91x_accept_async(sock, _wius_tcp_server_cb_accept) < 0)
    {
        LOG_E("Accept failed: %s", strerror(errno));
        sl_si91x_shutdown(sock, 0);
        return;
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

void _wius_tcp_server_respond_udp_done_handler(int32_t socket, uint16_t length)
{
    LOG_I("Transmit on socket %d of length %u done", socket, length);
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

    server_addr.sin_addr.s_addr = msg->meta->dest_ip_addr.ipv4_address[0] |
                                  (msg->meta->dest_ip_addr.ipv4_address[1] << 8) |
                                  (msg->meta->dest_ip_addr.ipv4_address[2] << 16) |
                                  (msg->meta->dest_ip_addr.ipv4_address[3] << 24);
    server_addr.sin_port = htons(port);

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

        // LOG_D("  Sent UDP subpacket of size %d", sent);

        total_sent += sent;
    }
    // LOG_D("Sent UDP packet of size %d", response_length);

    // sl_si91x_shutdown(udp_sock, 0);
    // udp_sock = -1;

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

// ssize_t _upd_send_large_data(int socket, const uint8_t *buffer, size_t buffer_length, int32_t flags)
// {
//     ssize_t total_sent = 0;

//     if (buffer_length > 1472)
//     {
//         size_t iterations = buffer_length / 1472;
//         size_t packet_size = 1472;
//         size_t last_packet_size = 1472;

//         if (buffer_length > iterations * 1472)
//         {
//             iterations += 1;
//             last_packet_size = buffer_length - (iterations - 1) * 1472;
//         }

//         for (size_t it = 0; it < iterations; it++)
//         {
//             size_t current_packet_size = (it == (iterations - 1)) ? last_packet_size : packet_size;

//             int sent = sl_si91x_send(socket, buffer + total_sent, current_packet_size, flags);
//             if (sent < 0)
//             {
//                 LOG_E("Send failed: %s", strerror(errno));
//                 return -1;
//             }
//             total_sent += sent;
//         }
//     }
//     else
//     {
//         total_sent = sl_si91x_send(socket, buffer, buffer_length, flags);
//     }

//     return total_sent;
// }

sl_status_t wius_tcp_server_respond_data(wius_tcp_server_message_t *msg, uint8_t cmd_id, uint8_t *data, size_t data_length)
{
    sl_status_t status = SL_STATUS_OK;

    UNUSED_PARAMETER(cmd_id);

    // size_t num_packets = (data_length + 1400) / 1400;
    // uint8_t response[4];
    // response[0] = cmd_id;
    // memcpy(&response[1], "DT", 2);
    // response[3] = (uint8_t)num_packets;
    // CHECK_STATUS(wius_tcp_server_respond(msg, (char *)response, sizeof(response)));

    int sent = sl_si91x_send_large_data(msg->socket, data, data_length, 0);
    // int sent = _upd_send_large_data(msg->socket, data, data_length, 0);
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