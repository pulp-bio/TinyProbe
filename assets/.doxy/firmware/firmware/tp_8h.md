

# File tp.h



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**tp.h**](tp_8h.md)

[Go to the source code of this file](tp_8h_source.md)

_TinyProbe main header file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "wius_udp.h"`
* `#include "tp_buffer.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  osSemaphoreId\_t | [**sem\_fpga**](#variable-sem_fpga)  <br> |
|  [**tp\_buffer\_t**](structtp__buffer__t.md) | [**tp\_buf**](#variable-tp_buf)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**tp\_init**](#function-tp_init) (void) <br>_Initialize the FPGA (SPI, GPIOs, register values)_  |
|  sl\_status\_t | [**tp\_main\_thread**](#function-tp_main_thread) (void) <br>_TinyProbe main thread._  |




























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




### variable sem\_fpga 

```C++
osSemaphoreId_t sem_fpga;
```



Semaphore raised by FPGA interrupts 

        

<hr>



### variable tp\_buf 

```C++
tp_buffer_t tp_buf;
```



Buffer for storing acquired data 

        

<hr>
## Public Functions Documentation




### function tp\_init 

_Initialize the FPGA (SPI, GPIOs, register values)_ 
```C++
sl_status_t tp_init (
    void
) 
```





**Return value:**


* `SL_STATUS_OK` Success 
* `other` SPI, GPIO interrupt or register initialization failed 



        

<hr>



### function tp\_main\_thread 

_TinyProbe main thread._ 
```C++
sl_status_t tp_main_thread (
    void
) 
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/tp.h`

