

# File tp\_method\_ping.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_ping.c**](tp__method__ping_8c.md)

[Go to the documentation of this file](tp__method__ping_8c.md)


```C++

#include "tp_method_ping.h"

#include "wius_tcp.h"

methods_status tp_method_ping(const methods_ping_args *args, void *userdata)
{
    UNUSED(userdata);

    sl_status_t status = SL_STATUS_OK;
    wius_tcp_server_message_t *msg = userdata;

    if (args->probe_id != TP_PROBE_ID)
    {
        log_warn("Invalid probe ID: %d", args->probe_id);
        return methods_status_INVALID_STATE;
    }

    char reply[32] = {0};
    snprintf(reply, sizeof(reply), "TinyProbe %lu", args->probe_id);

    status = wius_tcp_server_respond_udp(msg, TP_UDP_PORT, (uint8_t *)reply, strlen(reply));
    if (SL_STATUS_OK != status)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    return methods_status_OK;
}
```


