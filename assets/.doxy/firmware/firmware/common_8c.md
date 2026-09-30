

# File common.c



[**FileList**](files.md) **>** [**common**](dir_85edcc1f099af2a701a791767791d401.md) **>** [**common.c**](common_8c.md)

[Go to the source code of this file](common_8c_source.md)

_Common source file._ [More...](#detailed-description)

* `#include "common.h"`
* `#include "os_tick.h"`
* `#include "sl_si91x_clock_manager.h"`
* `#include "SEGGER_RTT.h"`
* `#include "log.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  uint32\_t | [**\_common\_ticks\_mult**](#variable-_common_ticks_mult)   = `0`<br> |


## Public Static Attributes

| Type | Name |
| ---: | :--- |
|  uint32\_t | [**\_common\_core\_clock\_hz**](#variable-_common_core_clock_hz)   = `0`<br> |














## Public Functions

| Type | Name |
| ---: | :--- |
|  int | [**\_log\_callback**](#function-_log_callback) (const char \* str, int len) <br> |
|  void | [**common\_init**](#function-common_init) (void) <br>_Initialize some common stuff._  |
|  void | [**common\_tick\_update**](#function-common_tick_update) (void) <br>_Update the common tick._  |
|  uint32\_t | [**core\_clock\_hz**](#function-core_clock_hz) (void) <br>_Get the current core clock in Hz._  |
|  void | [**delay\_ms**](#function-delay_ms) (uint32\_t ms) <br>_Delay for a given number of milliseconds._  |
|  void | [**delay\_ns**](#function-delay_ns) (uint64\_t ns) <br>_Delay for a given number of nanoseconds._  |
|  sl\_status\_t | [**log\_status**](#function-log_status) (const char \* file, int line, sl\_status\_t status) <br>_Log an error message with file and line information._  |
|  uint32\_t | [**time\_ms**](#function-time_ms) (void) <br>_Get the current time in milliseconds._  |




























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Attributes Documentation




### variable \_common\_ticks\_mult 

```C++
uint32_t _common_ticks_mult;
```




<hr>
## Public Static Attributes Documentation




### variable \_common\_core\_clock\_hz 

```C++
uint32_t _common_core_clock_hz;
```




<hr>
## Public Functions Documentation




### function \_log\_callback 

```C++
int _log_callback (
    const char * str,
    int len
) 
```




<hr>



### function common\_init 

_Initialize some common stuff._ 
```C++
void common_init (
    void
) 
```




<hr>



### function common\_tick\_update 

_Update the common tick._ 
```C++
void common_tick_update (
    void
) 
```




<hr>



### function core\_clock\_hz 

_Get the current core clock in Hz._ 
```C++
uint32_t core_clock_hz (
    void
) 
```





**Returns:**

Current core clock in Hz 




        

<hr>



### function delay\_ms 

_Delay for a given number of milliseconds._ 
```C++
void delay_ms (
    uint32_t ms
) 
```





**Parameters:**


* `ms` Number of milliseconds to delay 



        

<hr>



### function delay\_ns 

_Delay for a given number of nanoseconds._ 
```C++
void delay_ns (
    uint64_t ns
) 
```





**Parameters:**


* `ns` Number of nanoseconds to delay



**Note:**

This function is not very accurate 




        

<hr>



### function log\_status 

_Log an error message with file and line information._ 
```C++
sl_status_t log_status (
    const char * file,
    int line,
    sl_status_t status
) 
```





**Parameters:**


* `file` File name 
* `line` Line number 
* `status` Status to log



**Returns:**

Propagated status 




        

<hr>



### function time\_ms 

_Get the current time in milliseconds._ 
```C++
uint32_t time_ms (
    void
) 
```





**Returns:**

Current time in milliseconds 




        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/common/common.c`

