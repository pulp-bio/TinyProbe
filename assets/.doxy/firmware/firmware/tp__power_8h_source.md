

# File tp\_power.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_power.h**](tp__power_8h.md)

[Go to the documentation of this file](tp__power_8h.md)


```C++

#pragma once

#include "common.h"

typedef enum tp_power_domain
{
    TP_POWER_DOMAIN_LVDS_2_5V = 0, 
    TP_POWER_DOMAIN_POS_HV,        
    TP_POWER_DOMAIN_NEG_HV,        
    TP_POWER_DOMAIN_NEG_5V,        
    TP_POWER_DOMAIN_PLL_PWD        
} tp_power_domain_t;

void tp_power_init(void);

void tp_power_on(void);

void tp_power_set(tp_power_domain_t domain, bool enabled);
```


