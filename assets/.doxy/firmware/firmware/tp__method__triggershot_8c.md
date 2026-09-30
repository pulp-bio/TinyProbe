

# File tp\_method\_triggershot.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_triggershot.c**](tp__method__triggershot_8c.md)

[Go to the source code of this file](tp__method__triggershot_8c_source.md)

_TinyProbe Trigger Shot method implementation file._ [More...](#detailed-description)

* `#include "tp_method_triggershot.h"`
* `#include "tp.h"`
* `#include "tp_fpga.h"`
* `#include "tp_power.h"`
* `#include "wius_spi.h"`























## Public Static Attributes

| Type | Name |
| ---: | :--- |
|  uint8\_t | [**tx\_dummy**](#variable-tx_dummy)   = `{0}`<br> |














## Public Functions

| Type | Name |
| ---: | :--- |
|  methods\_status | [**tp\_method\_triggershot**](#function-tp_method_triggershot) (const methods\_triggershot\_args \* args, void \* userdata) <br>_JSON-RPC method handler for the "triggershot" method._  |


## Public Static Functions

| Type | Name |
| ---: | :--- |
|  sl\_status\_t | [**\_tp\_restore\_callback\_power**](#function-_tp_restore_callback_power) (bool \* callback\_powered\_down) <br> |
|  sl\_status\_t | [**\_tp\_transmit\_packages**](#function-_tp_transmit_packages) (uint32\_t shot\_index, uint16\_t num\_packets, uint16\_t callback\_id, bool \* callback\_powered\_down) <br> |


























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich 




**Author:**

Sergei Vostrikov, ETH Zürich




    
## Public Static Attributes Documentation




### variable tx\_dummy 

```C++
uint8_t tx_dummy[TP_BUFFER_SIZE];
```




<hr>
## Public Functions Documentation




### function tp\_method\_triggershot 

_JSON-RPC method handler for the "triggershot" method._ 
```C++
methods_status tp_method_triggershot (
    const methods_triggershot_args * args,
    void * userdata
) 
```





**Parameters:**


* `args` Command arguments struct 
* `userdata` User data pointer



**Returns:**

OK if method executed successfully, otherwise an error code 




        

<hr>
## Public Static Functions Documentation




### function \_tp\_restore\_callback\_power 

```C++
static sl_status_t _tp_restore_callback_power (
    bool * callback_powered_down
) 
```




<hr>



### function \_tp\_transmit\_packages 

```C++
static sl_status_t _tp_transmit_packages (
    uint32_t shot_index,
    uint16_t num_packets,
    uint16_t callback_id,
    bool * callback_powered_down
) 
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/methods/tp_method_triggershot.c`

