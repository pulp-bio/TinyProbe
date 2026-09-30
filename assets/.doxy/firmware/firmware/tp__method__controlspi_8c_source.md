

# File tp\_method\_controlspi.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_controlspi.c**](tp__method__controlspi_8c.md)

[Go to the documentation of this file](tp__method__controlspi_8c.md)


```C++

#include "tp_method_controlspi.h"

#include "tp_mux.h"

methods_status tp_method_controlspi(const methods_controlspi_args *args, void *userdata)
{
    UNUSED(userdata);

    tp_mux_select((tp_mux_t)args->domain);

    return methods_status_OK;
}
```


