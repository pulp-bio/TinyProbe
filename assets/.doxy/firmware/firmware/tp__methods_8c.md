

# File tp\_methods.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**tp\_methods.c**](tp__methods_8c.md)

[Go to the source code of this file](tp__methods_8c_source.md)

_TinyProbe methods implementation file._ [More...](#detailed-description)

* `#include "tp_methods.h"`
* `#include "sl_si91x_clock_manager.h"`
* `#include <pb_decode.h>`
* `#include <pb_encode.h>`
* `#include "methods.pb.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  methods\_request | [**req**](#variable-req)   = `methods\_request\_init\_default`<br> |
|  uint8\_t | [**response\_data**](#variable-response_data)  <br> |
|  methods\_response | [**rsp**](#variable-rsp)   = `methods\_response\_init\_default`<br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**tp\_methods\_handle**](#function-tp_methods_handle) ([**wius\_tcp\_server\_message\_t**](wius__tcp_8h.md#typedef-wius_tcp_server_message_t) \* request, void(\*)(const char \*response, size\_t response\_len) sender) <br>_Export all TinyProbe methods._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**X**](tp__methods_8c.md#define-x) (name) `/* multi line expression */`<br> |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich 




**Author:**

Sergei Vostrikov, ETH Zürich




    
## Public Attributes Documentation




### variable req 

```C++
methods_request req;
```




<hr>



### variable response\_data 

```C++
uint8_t response_data[methods_response_size];
```




<hr>



### variable rsp 

```C++
methods_response rsp;
```




<hr>
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





### define X 

```C++
#define X (
    name
) `/* multi line expression */`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/tp_methods.c`

