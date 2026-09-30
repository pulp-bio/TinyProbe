

# File tp\_method\_controlpower.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_controlpower.c**](tp__method__controlpower_8c.md)

[Go to the documentation of this file](tp__method__controlpower_8c.md)


```C++

#include "tp_method_controlpower.h"

#include "tp_power.h"

methods_status tp_method_controlpower(const methods_controlpower_args *args, void *userdata)
{
    UNUSED(userdata);

    tp_power_set((tp_power_domain_t)args->domain, args->enable);

    return methods_status_OK;
}
```


