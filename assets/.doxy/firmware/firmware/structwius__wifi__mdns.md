

# Struct wius\_wifi\_mdns



[**ClassList**](annotated.md) **>** [**wius\_wifi\_mdns**](structwius__wifi__mdns.md)



_WiFi mDNS service structure._ 

* `#include <wius_wifi.h>`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  sl\_mdns\_t | [**handle**](#variable-handle)  <br> |
|  char \* | [**host\_name**](#variable-host_name)  <br> |
|  uint16\_t | [**port**](#variable-port)  <br> |
|  char \* | [**protocol**](#variable-protocol)  <br> |
|  char \* | [**service\_message**](#variable-service_message)  <br> |
|  char \* | [**service\_name**](#variable-service_name)  <br> |












































## Public Attributes Documentation




### variable handle 

```C++
sl_mdns_t wius_wifi_mdns::handle;
```



mDNS handle 

        

<hr>



### variable host\_name 

```C++
char* wius_wifi_mdns::host_name;
```



Host name string (without .local) 

        

<hr>



### variable port 

```C++
uint16_t wius_wifi_mdns::port;
```



Service port number 

        

<hr>



### variable protocol 

```C++
char* wius_wifi_mdns::protocol;
```



Protocol string ("udp" or "tcp") 

        

<hr>



### variable service\_message 

```C++
char* wius_wifi_mdns::service_message;
```



Service message string 

        

<hr>



### variable service\_name 

```C++
char* wius_wifi_mdns::service_name;
```



Service name string 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_wifi.h`

