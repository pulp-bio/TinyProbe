

# File tp\_methods.h

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**tp\_methods.h**](tp__methods_8h.md)

[Go to the documentation of this file](tp__methods_8h.md)


```C++

#pragma once

#include "common.h"
#include "wius_tcp.h"

#include "methods/tp_method_controlpower.h"
#include "methods/tp_method_controlspi.h"
#include "methods/tp_method_delayms.h"
#include "methods/tp_method_delayns.h"
#include "methods/tp_method_ping.h"
#include "methods/tp_method_setloglevel.h"
#include "methods/tp_method_triggershot.h"
#include "methods/tp_method_writeafe.h"
#include "methods/tp_method_writefpga.h"
#include "methods/tp_method_writetx.h"

#define TP_METHODS \
    X(controlpower) \
    X(controlspi) \
    X(delayms) \
    X(delayns) \
    X(ping) \
    X(setloglevel) \
    X(triggershot) \
    X(writeafe) \
    X(writefpga) \
    X(writetx)

void tp_methods_handle(wius_tcp_server_message_t *request, void (*sender)(const char *response, size_t response_len));
```


