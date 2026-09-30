

# File wius\_wifi.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_wifi.h**](wius__wifi_8h.md)

[Go to the documentation of this file](wius__wifi_8h.md)


```C++

#pragma once

#include "common.h"

#include "sl_mdns.h"

typedef enum wius_wifi_performance_profile
{
    WIUS_PERF_PROFILE_HIGHSPEED, 
    WIUS_PERF_PROFILE_LOWPOWER   
} wius_wifi_performance_profile_t;

typedef struct wius_wifi_mdns
{
    sl_mdns_t handle;      
    char *protocol;        
    char *host_name;       
    char *service_name;    
    char *service_message; 
    uint16_t port;         
} wius_wifi_mdns_t;

sl_status_t wius_wifi_init(void);

sl_status_t wius_wifi_deinit(void);

sl_status_t wius_wifi_mdns_init(wius_wifi_mdns_t *mdns);

sl_status_t wius_wifi_mdns_add(wius_wifi_mdns_t *mdns);

sl_status_t wius_wifi_set_performance_profile(wius_wifi_performance_profile_t profile);
```


