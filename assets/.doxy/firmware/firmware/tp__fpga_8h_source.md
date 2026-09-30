

# File tp\_fpga.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_fpga.h**](tp__fpga_8h.md)

[Go to the documentation of this file](tp__fpga_8h.md)


```C++

#pragma once

#include "common.h"

sl_status_t tp_fpga_init(void);

sl_status_t tp_fpga_write_reg(uint32_t reg_value, uint8_t reg_addr);

sl_status_t tp_fpga_write_reg_safe(uint32_t reg_value, uint8_t reg_addr);

sl_status_t tp_fpga_write_cfg(uint8_t value);

sl_status_t tp_fpga_send_read_reg_cmd(uint8_t reg_addr);

sl_status_t tp_fpga_read_fifo(uint8_t *tx_buf, uint8_t *rx_buf, uint32_t len, bool wait);

sl_status_t tp_fpga_read_cfg(uint8_t *value);

sl_status_t tp_fpga_send_cmd(uint8_t cmd, uint8_t *answer);

sl_status_t tp_fpga_trigger_shot(void);

sl_status_t tp_fpga_send_start(void);

sl_status_t tp_fpga_reset_multififo(void);

sl_status_t tp_fpga_empty_tx(void);

sl_status_t tp_fpga_en_read(void);
```


