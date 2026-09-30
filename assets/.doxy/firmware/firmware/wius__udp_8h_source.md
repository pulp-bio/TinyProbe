

# File wius\_udp.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_udp.h**](wius__udp_8h.md)

[Go to the documentation of this file](wius__udp_8h.md)


```C++

#pragma once

#include "socket.h"

#include "common.h"

typedef struct wius_udp
{
    bool connected;                    
    int socket;                        
    struct sockaddr_in server_address; 
} wius_udp_t;

void wius_udp_init(wius_udp_t *udp);

sl_status_t wius_udp_bind(wius_udp_t *udp, char *ip, int port);

sl_status_t wius_udp_close(wius_udp_t *udp);

sl_status_t wius_udp_send(wius_udp_t *udp, const uint8_t *data, size_t data_len);

sl_status_t wius_udp_sendto(wius_udp_t *udp, const uint8_t *data, size_t data_len,
                            char *ip, int port);

sl_status_t wius_udp_receive(wius_udp_t *udp, uint8_t *buffer, size_t buffer_len, ssize_t *received_len,
                             int32_t timeout_ms);

sl_status_t wius_udp_receivefrom(wius_udp_t *udp, uint8_t *buffer, size_t buffer_len, ssize_t *received_len,
                                 char *ip, size_t ip_len, int *port, int32_t timeout_ms);
```


