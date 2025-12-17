/**
 * @file wius_udp.c
 *
 * @brief WiUS UDP implementation source file
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

#include "wius_udp.h"

#include "errno.h"
#include "sl_net.h"
#include "sl_si91x_driver.h"
#include <netinet_in.h>

#define MAX_PACKET_SIZE 1472

ssize_t _udp_sendto_fragmented(int fd, const void *data, size_t data_len,
                               int flags, const struct sockaddr *to_addr, socklen_t to_addr_len);

void wius_udp_init(wius_udp_t *udp)
{
    udp->connected = false;
    udp->socket = -1;

    udp->server_address.sin_family = -1;
    udp->server_address.sin_port = -1;
    udp->server_address.sin_addr.s_addr = -1;
}

sl_status_t wius_udp_bind(wius_udp_t *udp, char *ip, int port)
{
    if (udp->connected)
    {
        return SL_STATUS_SI91X_SOCKET_ALREADY_OPEN;
    }

    udp->socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (0 > udp->socket)
    {
        return SL_STATUS_SI91X_SOCKET_NOT_CREATED;
    }

    udp->connected = true;

    udp->server_address.sin_family = AF_INET;
    udp->server_address.sin_port = port;
    sl_net_inet_addr(ip, &udp->server_address.sin_addr.s_addr);

    int status = bind(udp->socket, (struct sockaddr *)&udp->server_address,
                      sizeof(udp->server_address));
    if (0 > status)
    {
        wius_udp_close(udp);
        return SL_STATUS_SI91X_SOCKET_NOT_CONNECTED;
    }

    return SL_STATUS_OK;
}

sl_status_t wius_udp_close(wius_udp_t *udp)
{
    if (!udp->connected)
    {
        return SL_STATUS_SI91X_SOCKET_NOT_CONNECTED;
    }

    close(udp->socket);

    udp->connected = false;

    wius_udp_init(udp);

    return SL_STATUS_OK;
}

sl_status_t wius_udp_send(wius_udp_t *udp, const uint8_t *data, size_t data_len)
{
    if (!udp->connected)
    {
        return SL_STATUS_SI91X_SOCKET_NOT_CONNECTED;
    }

    int bytes_sent = _udp_sendto_fragmented(udp->socket, data, data_len, 0,
                                            (struct sockaddr *)&udp->server_address,
                                            sizeof(udp->server_address));
    if (0 > bytes_sent)
    {
        return SL_STATUS_SI91X_IO_FAIL;
    }

    return SL_STATUS_OK;
}

sl_status_t wius_udp_sendto(wius_udp_t *udp, const uint8_t *data, size_t data_len,
                            char *ip, int port)
{
    if (!udp->connected)
    {
        return SL_STATUS_SI91X_SOCKET_NOT_CONNECTED;
    }

    struct sockaddr_in client_address;
    client_address.sin_family = AF_INET;
    client_address.sin_port = port;
    sl_net_inet_addr(ip, &client_address.sin_addr.s_addr);

    int bytes_sent = _udp_sendto_fragmented(udp->socket, data, data_len, 0,
                                            (struct sockaddr *)&client_address,
                                            sizeof(client_address));
    if (0 > bytes_sent)
    {
        return SL_STATUS_SI91X_IO_FAIL;
    }

    return SL_STATUS_OK;
}

sl_status_t wius_udp_receive(wius_udp_t *udp, uint8_t *buffer, size_t buffer_len, ssize_t *received_len, int32_t timeout_ms)
{
    if (!udp->connected)
    {
        return SL_STATUS_SI91X_SOCKET_NOT_CONNECTED;
    }

    if (buffer == NULL || received_len == NULL)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    if (timeout_ms > 0)
    {
        struct timeval tv;
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;
        setsockopt(udp->socket, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv,
                   sizeof(tv));
    }

    struct sockaddr from_addr;
    socklen_t from_addr_len = sizeof(from_addr);
    ssize_t len = recvfrom(udp->socket, buffer, buffer_len, 0, &from_addr,
                           &from_addr_len);
    if (len < 0)
    {
        *received_len = 0;
        return SL_STATUS_SI91X_IO_FAIL;
    }

    *received_len = len; // Set the actual received length

    return SL_STATUS_OK;
}

sl_status_t wius_udp_receivefrom(wius_udp_t *udp, uint8_t *buffer, size_t buffer_len, ssize_t *received_len,
                                 char *ip, size_t ip_len, int *port, int32_t timeout_ms)
{
    if (!udp->connected)
    {
        return SL_STATUS_SI91X_SOCKET_NOT_CONNECTED;
    }

    if (buffer == NULL || received_len == NULL)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    if (timeout_ms > 0)
    {
        struct timeval tv;
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;
        setsockopt(udp->socket, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv,
                   sizeof(tv));
    }

    struct sockaddr from_addr;
    socklen_t from_addr_len = sizeof(from_addr);
    ssize_t len = recvfrom(udp->socket, buffer, buffer_len, 0, &from_addr,
                           &from_addr_len);
    if (len < 0)
    {
        *received_len = 0;
        return SL_STATUS_SI91X_IO_FAIL;
    }

    *received_len = len; // Set the actual received length

    // if client socket is passed, replace port and ip
    if ((NULL != ip) && ip_len)
    {
        struct sockaddr_in *addr_in = (struct sockaddr_in *)&from_addr;

        uint8_t byte1 = (addr_in->sin_addr.s_addr & (0xFF << 24)) >> 24;
        uint8_t byte2 = (addr_in->sin_addr.s_addr & (0xFF << 16)) >> 16;
        uint8_t byte3 = (addr_in->sin_addr.s_addr & (0xFF << 8)) >> 8;
        uint8_t byte4 = (addr_in->sin_addr.s_addr & (0xFF << 0)) >> 0;

        snprintf(ip, ip_len, "%u.%u.%u.%u", byte4, byte3, byte2, byte1);
    }

    if ((NULL != port))
    {
        struct sockaddr_in *addr_in = (struct sockaddr_in *)&from_addr;

        *port = addr_in->sin_port;
    }

    return SL_STATUS_OK;
}

ssize_t _udp_sendto_fragmented(int fd, const void *data, size_t data_len,
                               int flags, const struct sockaddr *to_addr, socklen_t to_addr_len)
{
    ssize_t total_sent = 0;

    if (data_len > MAX_PACKET_SIZE)
    {
        size_t iterations = data_len / MAX_PACKET_SIZE;
        size_t packet_size = MAX_PACKET_SIZE;
        size_t last_packet_size = MAX_PACKET_SIZE;

        if (data_len > iterations * MAX_PACKET_SIZE)
        {
            iterations++;
            last_packet_size = data_len - (iterations - 1) * MAX_PACKET_SIZE;
        }

        for (size_t it = 0; it < iterations; it++)
        {
            int bytes_sent = sendto(fd, (uint8_t *)data + it * packet_size,
                                    it != iterations - 1 ? packet_size : last_packet_size,
                                    flags, to_addr, to_addr_len);

            if (bytes_sent < 0)
            {
                return bytes_sent;
            }

            total_sent += bytes_sent;
        }
    }
    else
    {
        total_sent = sendto(fd, (uint8_t *)data, data_len, flags, to_addr,
                            to_addr_len);
    }

    return total_sent;
}