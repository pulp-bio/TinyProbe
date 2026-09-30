

# File tp\_method\_writeafe.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_writeafe.c**](tp__method__writeafe_8c.md)

[Go to the documentation of this file](tp__method__writeafe_8c.md)


```C++

#include "tp_method_writeafe.h"

#include "tp_afe.h"

methods_status tp_method_writeafe(const methods_writeafe_args *args, void *userdata)
{
    UNUSED(userdata);

    sl_status_t status = SL_STATUS_OK;

    // log_debug("Writing %lu to %u (dtgc=%d)", args->value, args->address, args->dtgc);

    if (args->dtgc)
    {
        status = tp_afe_write_reg_dtgc(args->address, args->value);
    }
    else
    {
        status = tp_afe_write_reg(args->address, args->value);
    }
    if (SL_STATUS_OK != status)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    return methods_status_OK;
}
```


