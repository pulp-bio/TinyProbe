

# File tp\_tx.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_tx.h**](tp__tx_8h.md)

[Go to the documentation of this file](tp__tx_8h.md)


```C++

#pragma once

#include "common.h"

sl_status_t tp_tx_init(void);

sl_status_t tp_tx_write_reg(uint16_t address, uint32_t value);

sl_status_t tp_tx_write_reg_safe(uint16_t address, uint32_t value);

sl_status_t tp_tx_read_reg(uint16_t address, uint32_t *value);
```


