

# File wius\_udp.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_udp.h**](wius__udp_8h.md)

[Go to the source code of this file](wius__udp_8h_source.md)

_WiUS UDP implementation header file._ [More...](#detailed-description)

* `#include "socket.h"`
* `#include "common.h"`















## Classes

| Type | Name |
| ---: | :--- |
| struct | [**wius\_udp**](structwius__udp.md) <br>_UDP connection structure._  |


## Public Types

| Type | Name |
| ---: | :--- |
| typedef struct [**wius\_udp**](structwius__udp.md) | [**wius\_udp\_t**](#typedef-wius_udp_t)  <br>_UDP connection structure._  |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_udp\_bind**](#function-wius_udp_bind) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp, char \* ip, int port) <br>_Bind the UDP socket._  |
|  sl\_status\_t | [**wius\_udp\_close**](#function-wius_udp_close) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp) <br>_Close the UDP socket._  |
|  void | [**wius\_udp\_init**](#function-wius_udp_init) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp) <br>_Initialize the UDP connection._  |
|  sl\_status\_t | [**wius\_udp\_receive**](#function-wius_udp_receive) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp, uint8\_t \* buffer, size\_t buffer\_len, ssize\_t \* received\_len, int32\_t timeout\_ms) <br>_Receive data over a UDP connection._  |
|  sl\_status\_t | [**wius\_udp\_receivefrom**](#function-wius_udp_receivefrom) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp, uint8\_t \* buffer, size\_t buffer\_len, ssize\_t \* received\_len, char \* ip, size\_t ip\_len, int \* port, int32\_t timeout\_ms) <br>_Receive data over a UDP connection and retrieve the sender IP and port._  |
|  sl\_status\_t | [**wius\_udp\_send**](#function-wius_udp_send) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp, const uint8\_t \* data, size\_t data\_len) <br>_Send data over a UDP connection._  |
|  sl\_status\_t | [**wius\_udp\_sendto**](#function-wius_udp_sendto) ([**wius\_udp\_t**](wius__udp_8h.md#typedef-wius_udp_t) \* udp, const uint8\_t \* data, size\_t data\_len, char \* ip, int port) <br>_Send data over a UDP connection to a specific IP and port._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### typedef wius\_udp\_t 

_UDP connection structure._ 
```C++
typedef struct wius_udp  wius_udp_t;
```





**Note:**

To be filled by [**wius\_udp\_init**](wius__udp_8h.md#function-wius_udp_init) 




        

<hr>
## Public Functions Documentation




### function wius\_udp\_bind 

_Bind the UDP socket._ 
```C++
sl_status_t wius_udp_bind (
    wius_udp_t * udp,
    char * ip,
    int port
) 
```





**Parameters:**


* `udp` UDP connection structure 
* `ip` Server IP address 
* `port` Server port



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_SI91X_SOCKET_ALREADY_OPEN` Socket already binded 
* `SL_STATUS_SI91X_SOCKET_NOT_CREATED` Socket creation failed 
* `SL_STATUS_SI91X_SOCKET_NOT_CONNECTED` Socket binding failed 



        

<hr>



### function wius\_udp\_close 

_Close the UDP socket._ 
```C++
sl_status_t wius_udp_close (
    wius_udp_t * udp
) 
```





**Parameters:**


* `udp` UDP connection structure



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_SI91X_SOCKET_NOT_CONNECTED` Socket not binded 



        

<hr>



### function wius\_udp\_init 

_Initialize the UDP connection._ 
```C++
void wius_udp_init (
    wius_udp_t * udp
) 
```





**Parameters:**


* `udp` UDP connection structure



**Note:**

This function must be called before any other UDP function 




        

<hr>



### function wius\_udp\_receive 

_Receive data over a UDP connection._ 
```C++
sl_status_t wius_udp_receive (
    wius_udp_t * udp,
    uint8_t * buffer,
    size_t buffer_len,
    ssize_t * received_len,
    int32_t timeout_ms
) 
```





**Parameters:**


* `udp` UDP connection structure 
* `buffer` Buffer to store received data 
* `buffer_len` Buffer length 
* `received_len` Pointer to store the received data length 
* `timeout_ms` Timeout in milliseconds (set to &lt;= 0 for blocking)



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_SI91X_SOCKET_NOT_CONNECTED` Socket not binded 
* `SL_STATUS_INVALID_PARAMETER` buffer or received\_len is NULL 
* `SL_STATUS_SI91X_IO_FAIL` Receive failed 



        

<hr>



### function wius\_udp\_receivefrom 

_Receive data over a UDP connection and retrieve the sender IP and port._ 
```C++
sl_status_t wius_udp_receivefrom (
    wius_udp_t * udp,
    uint8_t * buffer,
    size_t buffer_len,
    ssize_t * received_len,
    char * ip,
    size_t ip_len,
    int * port,
    int32_t timeout_ms
) 
```





**Parameters:**


* `udp` UDP connection structure 
* `buffer` Buffer to store received data 
* `buffer_len` Buffer length 
* `received_len` Pointer to store the received data length 
* `ip` Buffer to store the sender IP address (at least 16 bytes) 
* `ip_len` IP buffer length (at least 16 bytes) 
* `port` Pointer to store the sender port 
* `timeout_ms` Timeout in milliseconds (set to &lt;= 0 for blocking)



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_SI91X_SOCKET_NOT_CONNECTED` Socket not binded 
* `SL_STATUS_INVALID_PARAMETER` buffer or received\_len is NULL 
* `SL_STATUS_SI91X_IO_FAIL` Receive failed 



        

<hr>



### function wius\_udp\_send 

_Send data over a UDP connection._ 
```C++
sl_status_t wius_udp_send (
    wius_udp_t * udp,
    const uint8_t * data,
    size_t data_len
) 
```





**Parameters:**


* `udp` UDP connection structure 
* `data` Data buffer 
* `data_len` Data length



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_SI91X_SOCKET_NOT_CONNECTED` Socket not binded 
* `SL_STATUS_SI91X_IO_FAIL` Send failed 



        

<hr>



### function wius\_udp\_sendto 

_Send data over a UDP connection to a specific IP and port._ 
```C++
sl_status_t wius_udp_sendto (
    wius_udp_t * udp,
    const uint8_t * data,
    size_t data_len,
    char * ip,
    int port
) 
```





**Parameters:**


* `udp` UDP connection structure 
* `data` Data buffer 
* `data_len` Data length 
* `ip` Destination IP address 
* `port` Destination port



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_SI91X_SOCKET_NOT_CONNECTED` Socket not binded 
* `SL_STATUS_SI91X_IO_FAIL` Send failed 



        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_udp.h`

