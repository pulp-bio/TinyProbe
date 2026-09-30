

# File wius\_tcp.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_tcp.h**](wius__tcp_8h.md)

[Go to the source code of this file](wius__tcp_8h_source.md)

_WiUS TCP implementation header file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "sl_si91x_socket.h"`















## Classes

| Type | Name |
| ---: | :--- |
| struct | [**wius\_tcp\_server\_message**](structwius__tcp__server__message.md) <br>_TCP connection message structure._  |


## Public Types

| Type | Name |
| ---: | :--- |
| typedef struct [**wius\_tcp\_server\_message**](structwius__tcp__server__message.md) | [**wius\_tcp\_server\_message\_t**](#typedef-wius_tcp_server_message_t)  <br>_TCP connection message structure._  |




## Public Attributes

| Type | Name |
| ---: | :--- |
|  osMessageQueueId\_t | [**wius\_tcp\_server\_queue**](#variable-wius_tcp_server_queue)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_tcp\_server\_deinit**](#function-wius_tcp_server_deinit) (void) <br>_Deinitialize the TCP server._  |
|  sl\_status\_t | [**wius\_tcp\_server\_init**](#function-wius_tcp_server_init) (void) <br>_Initialize the TCP server._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond**](#function-wius_tcp_server_respond) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, char \* response, size\_t response\_length) <br>_Send a response to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_data**](#function-wius_tcp_server_respond_data) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint8\_t cmd\_id, uint8\_t \* data, size\_t data\_length) <br>_Send data to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_error**](#function-wius_tcp_server_respond_error) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint8\_t cmd\_id, sl\_status\_t error\_code) <br>_Send an "Error" response to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_ok**](#function-wius_tcp_server_respond_ok) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint8\_t cmd\_id) <br>_Send an "OK" response to a TCP client._  |
|  sl\_status\_t | [**wius\_tcp\_server\_respond\_udp**](#function-wius_tcp_server_respond_udp) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* msg, uint16\_t port, uint8\_t \* response, size\_t response\_length) <br>_Send a UDP response to a specified IP and port._  |
|  sl\_status\_t | [**wius\_tcp\_server\_start**](#function-wius_tcp_server_start) (uint16\_t port) <br>_Start the TCP server on the specified port._  |
|  sl\_status\_t | [**wius\_tcp\_server\_stop**](#function-wius_tcp_server_stop) (void) <br>_Stop the TCP server._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**WIUS\_TCP\_SERVER\_MAX\_CLIENTS**](wius__tcp_8h.md#define-wius_tcp_server_max_clients)  `5`<br>_Maximum number of TCP server clients._  |
| define  | [**WIUS\_TCP\_SERVER\_MESSAGE\_DATA\_SIZE**](wius__tcp_8h.md#define-wius_tcp_server_message_data_size)  `1000`<br>_TCP server message data size._  |
| define  | [**WIUS\_TCP\_SERVER\_QUEUE\_SIZE**](wius__tcp_8h.md#define-wius_tcp_server_queue_size)  `10`<br>_TCP server message queue size._  |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### typedef wius\_tcp\_server\_message\_t 

_TCP connection message structure._ 
```C++
typedef struct wius_tcp_server_message  wius_tcp_server_message_t;
```




<hr>
## Public Attributes Documentation




### variable wius\_tcp\_server\_queue 

```C++
osMessageQueueId_t wius_tcp_server_queue;
```



TCP server message queue identifier 

        

<hr>
## Public Functions Documentation




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
## Macro Definition Documentation





### define WIUS\_TCP\_SERVER\_MAX\_CLIENTS 

_Maximum number of TCP server clients._ 
```C++
#define WIUS_TCP_SERVER_MAX_CLIENTS `5`
```




<hr>



### define WIUS\_TCP\_SERVER\_MESSAGE\_DATA\_SIZE 

_TCP server message data size._ 
```C++
#define WIUS_TCP_SERVER_MESSAGE_DATA_SIZE `1000`
```




<hr>



### define WIUS\_TCP\_SERVER\_QUEUE\_SIZE 

_TCP server message queue size._ 
```C++
#define WIUS_TCP_SERVER_QUEUE_SIZE `10`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_tcp.h`

