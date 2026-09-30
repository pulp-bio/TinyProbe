

# File wius\_power.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_power.h**](wius__power_8h.md)

[Go to the documentation of this file](wius__power_8h.md)


```C++

#pragma once

#include "common.h"

typedef enum wius_power_mode
{
    WIUS_POWER_MODE_LOW = 0, 
    WIUS_POWER_MODE_HIGH     
} wius_power_mode_t;

sl_status_t wius_power_init(void);

sl_status_t wius_power_set(wius_power_mode_t mode);
```


