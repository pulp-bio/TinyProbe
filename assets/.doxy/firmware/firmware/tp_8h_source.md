

# File tp.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**tp.h**](tp_8h.md)

[Go to the documentation of this file](tp_8h.md)


```C++

#pragma once

#include "common.h"
#include "wius_udp.h"
#include "tp_buffer.h"

extern osSemaphoreId_t sem_fpga; 
extern tp_buffer_t tp_buf; 
sl_status_t tp_init(void);

sl_status_t tp_main_thread(void);
```


