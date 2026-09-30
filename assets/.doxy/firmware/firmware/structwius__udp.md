

# Struct wius\_udp



[**ClassList**](annotated.md) **>** [**wius\_udp**](structwius__udp.md)



_UDP connection structure._ [More...](#detailed-description)

* `#include <wius_udp.h>`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  bool | [**connected**](#variable-connected)  <br> |
|  struct sockaddr\_in | [**server\_address**](#variable-server_address)  <br> |
|  int | [**socket**](#variable-socket)  <br> |












































## Detailed Description




**Note:**

To be filled by [**wius\_udp\_init**](wius__udp_8h.md#function-wius_udp_init) 




    
## Public Attributes Documentation




### variable connected 

```C++
bool wius_udp::connected;
```



Connection status flag 

        

<hr>



### variable server\_address 

```C++
struct sockaddr_in wius_udp::server_address;
```



Server address structure 

        

<hr>



### variable socket 

```C++
int wius_udp::socket;
```



Socket file descriptor 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_udp.h`

