

# File tp\_methods.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**tp\_methods.h**](tp__methods_8h.md)

[Go to the source code of this file](tp__methods_8h_source.md)

_TinyProbe methods header file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "wius_tcp.h"`
* `#include "methods/tp_method_controlpower.h"`
* `#include "methods/tp_method_controlspi.h"`
* `#include "methods/tp_method_delayms.h"`
* `#include "methods/tp_method_delayns.h"`
* `#include "methods/tp_method_ping.h"`
* `#include "methods/tp_method_setloglevel.h"`
* `#include "methods/tp_method_triggershot.h"`
* `#include "methods/tp_method_writeafe.h"`
* `#include "methods/tp_method_writefpga.h"`
* `#include "methods/tp_method_writetx.h"`





































## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**tp\_methods\_handle**](#function-tp_methods_handle) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* request, void(\*)(const char \*response, size\_t response\_len) sender) <br>_Export all TinyProbe methods._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**TP\_METHODS**](tp__methods_8h.md#define-tp_methods)  `/* multi line expression */`<br>_All TinyProbe methods must be listed here._  |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich 




**Author:**

Sergei Vostrikov, ETH Zürich




    
## Public Functions Documentation




### function tp\_methods\_handle 

_Export all TinyProbe methods._ 
```C++
void tp_methods_handle (
    wius_tcp_server_message_t * request,
    void(*)(const char *response, size_t response_len) sender
) 
```




<hr>
## Macro Definition Documentation





### define TP\_METHODS 

_All TinyProbe methods must be listed here._ 
```C++
#define TP_METHODS `/* multi line expression */`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/tp_methods.h`

