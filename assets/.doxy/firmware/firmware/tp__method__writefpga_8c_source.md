

# File tp\_method\_writefpga.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_writefpga.c**](tp__method__writefpga_8c.md)

[Go to the documentation of this file](tp__method__writefpga_8c.md)


```C++

#include "tp_method_writefpga.h"

#include "tp_fpga.h"

methods_status tp_method_writefpga(const methods_writefpga_args *args, void *userdata)
{
    UNUSED(userdata);

    sl_status_t status = SL_STATUS_OK;

    // log_debug("Writing %lu to %u", args->value, args->address);

    status = tp_fpga_write_reg(args->value, args->address);
    if (SL_STATUS_OK != status)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    return methods_status_OK;
}
```


