

# File wius\_wifi.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_wifi.h**](wius__wifi_8h.md)

[Go to the source code of this file](wius__wifi_8h_source.md)

_WiUS WiFi implementation header file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "sl_mdns.h"`















## Classes

| Type | Name |
| ---: | :--- |
| struct | [**wius\_wifi\_mdns**](structwius__wifi__mdns.md) <br>_WiFi mDNS service structure._  |


## Public Types

| Type | Name |
| ---: | :--- |
| typedef struct [**wius\_wifi\_mdns**](structwius__wifi__mdns.md) | [**wius\_wifi\_mdns\_t**](#typedef-wius_wifi_mdns_t)  <br>_WiFi mDNS service structure._  |
| enum  | [**wius\_wifi\_performance\_profile**](#enum-wius_wifi_performance_profile)  <br>_WiFi performance profile enumeration._  |
| typedef enum [**wius\_wifi\_performance\_profile**](wius__wifi_8h.md#enum-wius_wifi_performance_profile) | [**wius\_wifi\_performance\_profile\_t**](#typedef-wius_wifi_performance_profile_t)  <br>_WiFi performance profile enumeration._  |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**wius\_wifi\_deinit**](#function-wius_wifi_deinit) (void) <br>_Deinitialize the WiFi client interface._  |
|  sl\_status\_t | [**wius\_wifi\_init**](#function-wius_wifi_init) (void) <br>_Initialize the WiFi client interface._  |
|  sl\_status\_t | [**wius\_wifi\_mdns\_add**](#function-wius_wifi_mdns_add) ([**wius\_wifi\_mdns\_t**](wius__wifi_8h.md#typedef-wius_wifi_mdns_t) \* mdns) <br>_Add an mDNS service._  |
|  sl\_status\_t | [**wius\_wifi\_mdns\_init**](#function-wius_wifi_mdns_init) ([**wius\_wifi\_mdns\_t**](wius__wifi_8h.md#typedef-wius_wifi_mdns_t) \* mdns) <br>_Initialize an mDNS service structure._  |
|  sl\_status\_t | [**wius\_wifi\_set\_performance\_profile**](#function-wius_wifi_set_performance_profile) ([**wius\_wifi\_performance\_profile\_t**](wius__wifi_8h.md#typedef-wius_wifi_performance_profile_t) profile) <br>_Set the WiFi performance profile._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### typedef wius\_wifi\_mdns\_t 

_WiFi mDNS service structure._ 
```C++
typedef struct wius_wifi_mdns  wius_wifi_mdns_t;
```




<hr>



### enum wius\_wifi\_performance\_profile 

_WiFi performance profile enumeration._ 
```C++
enum wius_wifi_performance_profile {
    WIUS_PERF_PROFILE_HIGHSPEED,
    WIUS_PERF_PROFILE_LOWPOWER
};
```




<hr>



### typedef wius\_wifi\_performance\_profile\_t 

_WiFi performance profile enumeration._ 
```C++
typedef enum wius_wifi_performance_profile  wius_wifi_performance_profile_t;
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

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_wifi.h`

