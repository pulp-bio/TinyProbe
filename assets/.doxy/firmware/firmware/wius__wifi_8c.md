

# File wius\_wifi.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_wifi.c**](wius__wifi_8c.md)

[Go to the source code of this file](wius__wifi_8c_source.md)

_WiUS WiFi implementation source file._ [More...](#detailed-description)

* `#include "wius_wifi.h"`
* `#include <string.h>`
* `#include "sl_utility.h"`
* `#include "sl_wifi.h"`
* `#include "sl_net.h"`
* `#include "sl_net_default_values.h"`
* `#include "sl_net_wifi_types.h"`























## Public Static Attributes

| Type | Name |
| ---: | :--- |
|  const sl\_wifi\_device\_configuration\_t | [**station\_init\_configuration**](#variable-station_init_configuration)   = `/* multi line expression */`<br> |
|  const sl\_net\_wifi\_psk\_credential\_entry\_t | [**wifi\_client\_credential**](#variable-wifi_client_credential)   = `/* multi line expression */`<br> |
|  const sl\_net\_wifi\_client\_profile\_t | [**wifi\_client\_profile**](#variable-wifi_client_profile)   = `/* multi line expression */`<br> |














## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_wifi\_deinit**](#function-wius_wifi_deinit) (void) <br>_Deinitialize the WiFi client interface._  |
|  sl\_status\_t | [**wius\_wifi\_init**](#function-wius_wifi_init) (void) <br>_Initialize the WiFi client interface._  |
|  sl\_status\_t | [**wius\_wifi\_mdns\_add**](#function-wius_wifi_mdns_add) ([**wius\_wifi\_mdns\_t**](wius__wifi_8h.md#typedef-wius_wifi_mdns_t) \* mdns) <br>_Add an mDNS service._  |
|  sl\_status\_t | [**wius\_wifi\_mdns\_init**](#function-wius_wifi_mdns_init) ([**wius\_wifi\_mdns\_t**](wius__wifi_8h.md#typedef-wius_wifi_mdns_t) \* mdns) <br>_Initialize an mDNS service structure._  |
|  sl\_status\_t | [**wius\_wifi\_set\_performance\_profile**](#function-wius_wifi_set_performance_profile) ([**wius\_wifi\_performance\_profile\_t**](wius__wifi_8h.md#typedef-wius_wifi_performance_profile_t) profile) <br>_Set the WiFi performance profile._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**WIUS\_WIFI\_FILTER\_BROADCAST**](wius__wifi_8c.md#define-wius_wifi_filter_broadcast)  `0`<br> |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Static Attributes Documentation




### variable station\_init\_configuration 

```C++
const sl_wifi_device_configuration_t station_init_configuration;
```




<hr>



### variable wifi\_client\_credential 

```C++
const sl_net_wifi_psk_credential_entry_t wifi_client_credential;
```




<hr>



### variable wifi\_client\_profile 

```C++
const sl_net_wifi_client_profile_t wifi_client_profile;
```




<hr>
## Public Functions Documentation




### function wius\_wifi\_deinit 

_Deinitialize the WiFi client interface._ 
```C++
sl_status_t wius_wifi_deinit (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` net deinitialization failed 



        

<hr>



### function wius\_wifi\_init 

_Initialize the WiFi client interface._ 
```C++
sl_status_t wius_wifi_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` net initialization or bring up failed 



        

<hr>



### function wius\_wifi\_mdns\_add 

_Add an mDNS service._ 
```C++
sl_status_t wius_wifi_mdns_add (
    wius_wifi_mdns_t * mdns
) 
```





**Parameters:**


* `mdns` Pointer to the mDNS service structure



**Return value:**


* `SL_STATUS_OK` Success 
* `other` mDNS service addition failed 



        

<hr>



### function wius\_wifi\_mdns\_init 

_Initialize an mDNS service structure._ 
```C++
sl_status_t wius_wifi_mdns_init (
    wius_wifi_mdns_t * mdns
) 
```





**Parameters:**


* `mdns` Pointer to the mDNS service structure



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_INVALID_PARAMETER` Invalid parameter (null pointer or invalid host name) 
* `other` mDNS or interface initialization failed 



        

<hr>



### function wius\_wifi\_set\_performance\_profile 

_Set the WiFi performance profile._ 
```C++
sl_status_t wius_wifi_set_performance_profile (
    wius_wifi_performance_profile_t profile
) 
```





**Parameters:**


* `profile` Pointer to the performance profile enumeration ([**wius\_wifi\_performance\_profile\_t**](wius__wifi_8h.md#typedef-wius_wifi_performance_profile_t))



**Return value:**


* `SL_STATUS_OK` Success 
* `SL_STATUS_INVALID_PARAMETER` Invalid performance profile 
* `SL_STATUS_SI91X_POWER_SAVE_NOT_SUPPORTED` Profile not applied 
* `other` Performance profile setting failed 



        

<hr>
## Macro Definition Documentation





### define WIUS\_WIFI\_FILTER\_BROADCAST 

```C++
#define WIUS_WIFI_FILTER_BROADCAST `0`
```



Whether to filter the WiFi broadcast 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_wifi.c`

