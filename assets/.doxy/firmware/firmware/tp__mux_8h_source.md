

# File tp\_mux.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_mux.h**](tp__mux_8h.md)

[Go to the documentation of this file](tp__mux_8h.md)


```C++

#pragma once

#include "common.h"

typedef enum tp_mux
{
    TP_MUX_PLL = 0b00,  
    TP_MUX_FPGA = 0b01, 
    TP_MUX_AFE = 0b10,  
    TP_MUX_TX = 0b11    
} tp_mux_t;

void tp_mux_init(void);

void tp_mux_select(tp_mux_t mux);
```


