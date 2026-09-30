

# File wius\_tcp.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_tcp.c**](wius__tcp_8c.md)

[Go to the documentation of this file](wius__tcp_8c.md)


```C++

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
            // log_trace("Added client socket %d at index %d", socket, (int)i);
            return (int)i;
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
            // log_trace("Removed client socket %d from index %d", socket, (int)i);
            sl_si91x_shutdown(socket, 0);
            return (int)i;
        }
    }
    return -1; // Socket not found
}

void _wius_tcp_server_cb_term(int socket, uint16_t port, uint32_t bytes_sent)
{
    UNUSED_PARAMETER(port);
    UNUSED_PARAMETER(bytes_sent);

    // Guard against accidentally shutting down the listening socket.
    if (socket == sock)
    {
        log_warn("Termination callback for listening socket %d; ignoring", socket);
        return;
    }

    // When disconnected, remove the client socket from the list
    if (_wius_tcp_server_remove_client(socket) < 0)
    {
        log_error("Terminated socket %d not found", socket);
    }

    // log_debug("Terminated connection on socket %d, %u bytes sent", socket, (unsigned)bytes_sent);
}

static void _wius_tcp_server_cb_rx(uint32_t socket, uint8_t *buffer, uint32_t length, const sl_si91x_socket_metadata_t *meta)
{
    UNUSED_PARAMETER(meta);

    // Parse and enqueue the received message
    wius_tcp_server_message_t msg;
    msg.socket = socket;
    msg.length = (length < WIUS_TCP_SERVER_MESSAGE_DATA_SIZE) ? length : WIUS_TCP_SERVER_MESSAGE_DATA_SIZE;
    memcpy(msg.data, buffer, msg.length);
    msg.meta = meta;

    // log_trace("Received data of length %d on socket %ld", msg.length, socket);

    if (osMessageQueuePut(wius_tcp_server_queue, &msg, 0, 0) != osOK)
    {
        log_warn("Failed to send message to queue");
    }
    // log_trace("Enqueued message of length %d on socket %ld", msg.length, socket);
}

static void _wius_tcp_server_cb_accept(int32_t socket, struct sockaddr *addr, uint8_t ip_version)
{
    UNUSED_PARAMETER(addr);
    UNUSED_PARAMETER(ip_version);

    // log_info("Accepted connection on socket %ld", socket);

    // Add the new client socket to the list
    if (_wius_tcp_server_add_client(socket) < 0)
    {
        log_error("No space for new client socket %ld, closing", socket);
    }

    // Continue accepting new connections, otherwise we only ever accept one
    if (sl_si91x_accept_async(sock, _wius_tcp_server_cb_accept) < 0)
    {
        log_error("Accept failed: %s", strerror(errno));
        if (sl_si91x_shutdown(sock, 0) < 0)
        {
            log_error("Failed to shutdown listening socket %d", sock);
        }
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
        if (sl_si91x_shutdown(sock, 1) < 0)
        {
            log_error("Failed to shutdown socket %d", sock);
        }
    }
    if (udp_sock >= 0)
    {
        if (sl_si91x_shutdown(udp_sock, 1) < 0)
        {
            log_error("Failed to shutdown UDP socket %d", udp_sock);
        }
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
        log_error("Socket creation failed: %s", strerror(errno));
        return SL_STATUS_FAIL;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = 0; // Bind to all interfaces
    server_addr.sin_port = htons(port);
    if (sl_si91x_bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        log_error("Bind failed: %s", strerror(errno));
        if (sl_si91x_shutdown(sock, 1) < 0)
        {
            log_error("Failed to shutdown socket %d", sock);
        }
        return SL_STATUS_FAIL;
    }

    if (sl_si91x_listen(sock, WIUS_TCP_SERVER_MAX_CLIENTS) < 0)
    {
        log_error("Listen failed: %s", strerror(errno));
        if (sl_si91x_shutdown(sock, 1) < 0)
        {
            log_error("Failed to shutdown socket %d", sock);
        }
        return SL_STATUS_FAIL;
    }

    if (sl_si91x_accept_async(sock, _wius_tcp_server_cb_accept) < 0)
    {
        log_error("Accept failed: %s", strerror(errno));
        if (sl_si91x_shutdown(sock, 1) < 0)
        {
            log_error("Failed to shutdown socket %d", sock);
        }
        return SL_STATUS_FAIL;
    }

    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_stop(void)
{
    if (sock >= 0)
    {
        if (sl_si91x_shutdown(sock, 1) < 0)
        {
            log_error("Failed to shutdown socket %d", sock);
        }
        sock = -1;
    }
    if (udp_sock >= 0)
    {
        if (sl_si91x_shutdown(udp_sock, 1) < 0)
        {
            log_error("Failed to shutdown UDP socket %d", udp_sock);
        }
        udp_sock = -1;
    }
    return SL_STATUS_OK;
}

sl_status_t wius_tcp_server_respond(wius_tcp_server_message_t *msg, char *response, size_t response_length)
{
    // log_trace("Responding to socket %d with %u bytes", msg->socket, (unsigned)response_length);
    if (sl_si91x_send_async(msg->socket, (uint8_t *)response, response_length, 0, NULL) < 0)
    {
        log_error("Error sending response on socket %d: %s", msg->socket, strerror(errno));
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

    log_warn("Unexpected data received on socket %lu", socket);
}

void _wius_tcp_server_respond_udp_done_handler(int32_t socket, uint16_t length)
{
    UNUSED_PARAMETER(socket);
    UNUSED_PARAMETER(length);

    // log_trace("Transmit on socket %d of length %u done", socket, length);
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
            log_error("Error creating UDP socket");
            return SL_STATUS_FAIL;
        }

        // This socket is only used for sending, so set high performance option which can improve throughput
        uint32_t option = SLI_SI91X_HIGH_PERFORMANCE_SOCKET;
        if (sl_si91x_setsockopt(udp_sock, SOL_SOCKET, SL_SI91X_SO_HIGH_PERFORMANCE_SOCKET, &option, sizeof(option)) < 0)
        {
            log_error("Error setting socket options");
            sl_si91x_shutdown(udp_sock, 0);
            udp_sock = -1;
            return SL_STATUS_FAIL;
        }

        log_info("Created UDP socket %d for %u.%u.%u.%u:%u", udp_sock, msg->meta->dest_ip_addr.ipv4_address[0],
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
            log_error("Sendto failed: %s", strerror(errno));
            return SL_STATUS_FAIL;
        }

        total_sent += sent;
    }
    // log_trace("Sent UDP packet of size %d", response_length);

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
    // LOG_RET_STATUS(wius_tcp_server_respond(msg, (char *)response, sizeof(response)));

    // Here, we can use sl_si91x_send_large_data to send the data in chunks
    // This function handles splitting the data into MTU-sized packets internally but is not available for sendto
    int sent = sl_si91x_send_large_data(msg->socket, data, data_length, 0);
    if (sent < 0)
    {
        log_error("Send failed: %s", strerror(errno));
        return SL_STATUS_TRANSMIT;
    }
    if (sent != (int)data_length)
    {
        return SL_STATUS_TRANSMIT_INCOMPLETE;
    }

    return status;
}
```


