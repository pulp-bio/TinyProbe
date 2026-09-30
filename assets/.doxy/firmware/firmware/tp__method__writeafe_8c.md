

# File tp\_method\_writeafe.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**methods**](dir_9149039fde39a20b8d7b4b86d87b742c.md) **>** [**tp\_method\_writeafe.c**](tp__method__writeafe_8c.md)

[Go to the source code of this file](tp__method__writeafe_8c_source.md)

_TinyProbe AFE write method implementation file._ [More...](#detailed-description)

* `#include "tp_method_writeafe.h"`
* `#include "tp_afe.h"`





































## Public Functions

| Type | Name |
| ---: | :--- |
|  methods\_status | [**tp\_method\_writeafe**](#function-tp_method_writeafe) (const methods\_writeafe\_args \* args, void \* userdata) <br>_JSON-RPC method handler for the "writeafe" method._  |




























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




### function tp\_method\_writeafe 

_JSON-RPC method handler for the "writeafe" method._ 
```C++
methods_status tp_method_writeafe (
    const methods_writeafe_args * args,
    void * userdata
) 
```





**Parameters:**


* `args` Command arguments struct 
* `userdata` User data pointer



**Returns:**

OK if method executed successfully, otherwise an error code 




        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/methods/tp_method_writeafe.c`

