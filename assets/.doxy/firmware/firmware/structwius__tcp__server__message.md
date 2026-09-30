

# Struct wius\_tcp\_server\_message



[**ClassList**](annotated.md) **>** [**wius\_tcp\_server\_message**](structwius__tcp__server__message.md)



_TCP connection message structure._ 

* `#include <wius_tcp.h>`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  uint8\_t | [**data**](#variable-data)  <br> |
|  size\_t | [**length**](#variable-length)  <br> |
|  const sl\_si91x\_socket\_metadata\_t \* | [**meta**](#variable-meta)  <br> |
|  int | [**socket**](#variable-socket)  <br> |












































## Public Attributes Documentation




### variable data 

```C++
uint8_t wius_tcp_server_message::data[WIUS_TCP_SERVER_MESSAGE_DATA_SIZE];
```



Body data 

        

<hr>



### variable length 

```C++
size_t wius_tcp_server_message::length;
```



Length of the body data 

        

<hr>



### variable meta 

```C++
const sl_si91x_socket_metadata_t* wius_tcp_server_message::meta;
```



Metadata associated with the message 

        

<hr>



### variable socket 

```C++
int wius_tcp_server_message::socket;
```



Client socket 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_tcp.h`

