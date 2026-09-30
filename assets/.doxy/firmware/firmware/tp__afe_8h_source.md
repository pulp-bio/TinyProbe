

# File tp\_afe.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_afe.h**](tp__afe_8h.md)

[Go to the documentation of this file](tp__afe_8h.md)


```C++

#pragma once

#include "common.h"

typedef enum tp_afe_patt
{
    NORMAL_OPERATION = 0, 
    HALF_ZEROS_HALF_ONES, 
    ALTERN_ZERO_ONE,      
    CUSTOM,               
    ALL_ONES,             
    TOGGLE,               
    ALL_ZEROS,            
    RAMP                  
} tp_afe_patt_t;

sl_status_t tp_afe_init(void);

sl_status_t tp_afe_test_pattern(tp_afe_patt_t pattern);

sl_status_t tp_afe_write_reg(uint8_t address, uint16_t value);

sl_status_t tp_afe_write_reg_safe(uint8_t address, uint16_t value);

sl_status_t tp_afe_write_reg_dtgc(uint8_t address, uint16_t value);

sl_status_t tp_afe_write_reg_dtgc_safe(uint8_t address, uint16_t value);

sl_status_t tp_afe_read_reg(uint8_t address, uint16_t *value);

sl_status_t tp_afe_read_reg_dtgc(uint8_t address, uint16_t *value);
```


