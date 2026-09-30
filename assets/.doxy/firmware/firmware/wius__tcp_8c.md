

# File wius\_tcp.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_tcp.c**](wius__tcp_8c.md)

[Go to the source code of this file](wius__tcp_8c_source.md)

_WiUS TCP implementation source file._ [More...](#detailed-description)

* `#include "wius_tcp.h"`
* `#include <stdlib.h>`
* `#include <string.h>`
* `#include "errno.h"`
* `#include "netinet_in.h"`
* `#include "socket.h"`
* `#include "sl_si91x_core_utilities.h"`
* `#include "sl_si91x_socket_constants.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  int | [**client\_socks**](#variable-client_socks)  <br> |
|  struct sockaddr\_in | [**server\_addr**](#variable-server_addr)  <br> |
|  int | [**sock**](#variable-sock)  <br> |
|  int | [**udp\_sock**](#variable-udp_sock)  <br> |
|  osMessageQueueId\_t | [**wius\_tcp\_server\_queue**](#variable-wius_tcp_server_queue)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**\_wius\_tcp\_server\_cb\_term**](#function-_wius_tcp_server_cb_term) (int socket, uint16\_t port, uint32\_t bytes\_sent) <br>_Callback for remote termination of a socket._  |
|  void | [**\_wius\_tcp\_server\_respond\_udp\_done\_handler**](#function-_wius_tcp_server_respond_udp_done_handler) (int32\_t socket, uint16\_t length) <br>_Callback for UDP send completion._  |
|  sl\_status\_t | [**wius\_tcp\_server\_deinit**](#function-wius_tcp_server_deinit) (void) <br>_Deinitialize the TCP server._  |
|  sl\_status\_t | [**wius\_tcp\_server\_init**](#function-wius_tcp_server_init) (void) <br>_Initialize the TCP server._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond**](#function-wius_tcp_server_respond) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, char \* response, size\_t response\_length) <br>_Send a response to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_data**](#function-wius_tcp_server_respond_data) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint8\_t cmd\_id, uint8\_t \* data, size\_t data\_length) <br>_Send data to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_error**](#function-wius_tcp_server_respond_error) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint8\_t cmd\_id, sl\_status\_t error\_code) <br>_Send an "Error" response to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_ok**](#function-wius_tcp_server_respond_ok) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint8\_t cmd\_id) <br>_Send an "OK" response to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_udp**](#function-wius_tcp_server_respond_udp) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint16\_t port, uint8\_t \* response, size\_t response\_length) <br>_Send a UDP response to a specified IP and port._  |
|  sl\_status\_t | [**wius\_tcp\_server\_start**](#function-wius_tcp_server_start) (uint16\_t port) <br>_Start the TCP server on the specified port._  |
|  sl\_status\_t | [**wius\_tcp\_server\_stop**](#function-wius_tcp_server_stop) (void) <br>_Stop the TCP server._  |


## Public Static Functions

| Type | Name |
| ---: | :--- |
|  int | [**\_wius\_tcp\_server\_add\_client**](#function-_wius_tcp_server_add_client) (int socket) <br>_Add a client socket to the tracking list._  |
|  void | [**\_wius\_tcp\_server\_cb\_accept**](#function-_wius_tcp_server_cb_accept) (int32\_t socket, struct sockaddr \* addr, uint8\_t ip\_version) <br>_Callback for accepting a new client connection._  |
|  void | [**\_wius\_tcp\_server\_cb\_rx**](#function-_wius_tcp_server_cb_rx) (uint32\_t socket, uint8\_t \* buffer, uint32\_t length, const sl\_si91x\_socket\_metadata\_t \* meta) <br>_Callback for receiving data on the TCP server socket._  |
|  void | [**\_wius\_tcp\_server\_cb\_udp\_rx**](#function-_wius_tcp_server_cb_udp_rx) (uint32\_t socket, uint8\_t \* buffer, uint32\_t length, const sl\_si91x\_socket\_metadata\_t \* firmware\_socket\_response) <br>_Callback for receiving data on the UDP socket._  |
|  int | [**\_wius\_tcp\_server\_remove\_client**](#function-_wius_tcp_server_remove_client) (int socket) <br>_Remove a client socket from the tracking list and shut it down._  |


























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Attributes Documentation




### variable client\_socks 

```C++
int client_socks[WIUS_TCP_SERVER_MAX_CLIENTS];
```



Array of client sockets 

        

<hr>



### variable server\_addr 

```C++
struct sockaddr_in server_addr;
```



Server address structure 

        

<hr>



### variable sock 

```C++
int sock;
```



TCP server socket 

        

<hr>



### variable udp\_sock 

```C++
int udp_sock;
```



UDP socket for UDP responses 

        

<hr>



### variable wius\_tcp\_server\_queue 

```C++
osMessageQueueId_t wius_tcp_server_queue;
```



TCP server message queue identifier 

        

<hr>
## Public Functions Documentation




### function \_wius\_tcp\_server\_cb\_term 

_Callback for remote termination of a socket._ 
```C++
void _wius_tcp_server_cb_term (
    int socket,
    uint16_t port,
    uint32_t bytes_sent
) 
```





**Parameters:**


* `socket` Socket that was terminated 
* `port` Port number (unused) 
* `bytes_sent` Bytes sent before termination (unused) 



        

<hr>



### function \_wius\_tcp\_server\_respond\_udp\_done\_handler 

_Callback for UDP send completion._ 
```C++
void _wius_tcp_server_respond_udp_done_handler (
    int32_t socket,
    uint16_t length
) 
```





**Parameters:**


* `socket` Socket on which data was sent 
* `length` Length of the sent data



**Warning:**

This callback is actually never called but necessary for async sendto 




        

<hr>



### function wius\_tcp\_server\_deinit 

_Deinitialize the TCP server._ 
```C++
sl_status_t wius_tcp_server_deinit (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 



        

<hr>



### function wius\_tcp\_server\_init 

_Initialize the TCP server._ 
```C++
sl_status_t wius_tcp_server_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_ALLOCATION_FAILED` Memory allocation failed



**Note:**

This function must be called before any other TCP function 




        

<hr>



### function wius\_tcp\_server\_respond 

_Send a response to a TCP client._ 
```C++
sl_status_t wius_tcp_server_respond (
    wius_tcp_server_message_t * msg,
    char * response,
    size_t response_length
) 
```





**Parameters:**


* `msg` Pointer to the message structure containing client info 
* `response` Pointer to the response data 
* `response_length` Length of the response data



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Failure (During sending)



**Note:**

The server must be started with [**wius\_tcp\_server\_start**](wius__tcp_8h.md#function-wius_tcp_server_start) before sending responses 




**Note:**

The exact cause of failure can be found by reading the errno variable 




**Note:**

The msg parameter only has to contain the client socket 




        

<hr>



### function wius\_tcp\_server\_respond\_data 

_Send data to a TCP client._ 
```C++
sl_status_t wius_tcp_server_respond_data (
    wius_tcp_server_message_t * msg,
    uint8_t cmd_id,
    uint8_t * data,
    size_t data_length
) 
```





**Parameters:**


* `msg` Pointer to the message structure containing client info 
* `cmd_id` Command identifier 
* `data` Pointer to the data to send 
* `data_length` Length of the data to send



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_TRANSMIT` Failure during transmission 
* `SL_STATUS_TRANSMIT_INCOMPLETE` Incomplete transmission



**Note:**

The msg parameter only has to contain the client socket 




        

<hr>



### function wius\_tcp\_server\_respond\_error 

_Send an "Error" response to a TCP client._ 
```C++
sl_status_t wius_tcp_server_respond_error (
    wius_tcp_server_message_t * msg,
    uint8_t cmd_id,
    sl_status_t error_code
) 
```





**Parameters:**


* `msg` Pointer to the message structure containing client info 
* `cmd_id` Command identifier 
* `error_code` Error code to send



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Failure (During sending)



**Note:**

The msg parameter only has to contain the client socket 




        

<hr>



### function wius\_tcp\_server\_respond\_ok 

_Send an "OK" response to a TCP client._ 
```C++
sl_status_t wius_tcp_server_respond_ok (
    wius_tcp_server_message_t * msg,
    uint8_t cmd_id
) 
```





**Parameters:**


* `msg` Pointer to the message structure containing client info 
* `cmd_id` Command identifier



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Failure (During sending)



**Note:**

The msg parameter only has to contain the client socket 




        

<hr>



### function wius\_tcp\_server\_respond\_udp 

_Send a UDP response to a specified IP and port._ 
```C++
sl_status_t wius_tcp_server_respond_udp (
    wius_tcp_server_message_t * msg,
    uint16_t port,
    uint8_t * response,
    size_t response_length
) 
```





**Parameters:**


* `msg` Pointer to the message structure containing client info 
* `port` Destination port number 
* `response` Pointer to the response data 
* `response_length` Length of the response data



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Failure (During socket creation or sending)



**Note:**

The server must be started with [**wius\_tcp\_server\_start**](wius__tcp_8h.md#function-wius_tcp_server_start) before sending responses 




**Note:**

The exact cause of failure can be found by reading the errno variable 




**Note:**

The msg parameter only has to contain the destination IP address in its metadata 




        

<hr>



### function wius\_tcp\_server\_start 

_Start the TCP server on the specified port._ 
```C++
sl_status_t wius_tcp_server_start (
    uint16_t port
) 
```





**Parameters:**


* `port` Port number to listen on



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_FAIL` Failure (During socket creation, binding or listening)



**Note:**

The server must be initialized with [**wius\_tcp\_server\_init**](wius__tcp_8h.md#function-wius_tcp_server_init) before starting 




**Note:**

The exact cause of failure can be found by reading the errno variable 




        

<hr>



### function wius\_tcp\_server\_stop 

_Stop the TCP server._ 
```C++
sl_status_t wius_tcp_server_stop (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 



        

<hr>
## Public Static Functions Documentation




### function \_wius\_tcp\_server\_add\_client 

_Add a client socket to the tracking list._ 
```C++
static int _wius_tcp_server_add_client (
    int socket
) 
```





**Parameters:**


* `socket` Client socket to add



**Returns:**

int: Index where stored, -1 if no space (socket is shut down) 




        

<hr>



### function \_wius\_tcp\_server\_cb\_accept 

_Callback for accepting a new client connection._ 
```C++
static void _wius_tcp_server_cb_accept (
    int32_t socket,
    struct sockaddr * addr,
    uint8_t ip_version
) 
```





**Parameters:**


* `socket` New client socket 
* `addr` Address of the client 
* `ip_version` IP version of the client 



        

<hr>



### function \_wius\_tcp\_server\_cb\_rx 

_Callback for receiving data on the TCP server socket._ 
```C++
static void _wius_tcp_server_cb_rx (
    uint32_t socket,
    uint8_t * buffer,
    uint32_t length,
    const sl_si91x_socket_metadata_t * meta
) 
```





**Parameters:**


* `socket` Socket on which data was received 
* `buffer` Buffer containing the received data 
* `length` Length of the received data 
* `meta` Metadata associated with the message 



        

<hr>



### function \_wius\_tcp\_server\_cb\_udp\_rx 

_Callback for receiving data on the UDP socket._ 
```C++
static void _wius_tcp_server_cb_udp_rx (
    uint32_t socket,
    uint8_t * buffer,
    uint32_t length,
    const sl_si91x_socket_metadata_t * firmware_socket_response
) 
```





**Parameters:**


* `socket` Socket on which data was received 
* `buffer` Buffer containing the received data 
* `length` Length of the received data 
* `firmware_socket_response` Metadata associated with the message



**Warning:**

This callback will not process any received data, as the UDP socket is only used for sending responses 




        

<hr>



### function \_wius\_tcp\_server\_remove\_client 

_Remove a client socket from the tracking list and shut it down._ 
```C++
static int _wius_tcp_server_remove_client (
    int socket
) 
```





**Parameters:**


* `socket` Client socket to remove



**Returns:**

int: Index of removed socket, -1 if not found 




        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_tcp.c`

