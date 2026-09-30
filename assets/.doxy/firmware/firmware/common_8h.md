

# File common.h



[**FileList**](files.md) **>** [**common**](dir_85edcc1f099af2a701a791767791d401.md) **>** [**common.h**](common_8h.md)

[Go to the source code of this file](common_8h_source.md)

_Common header file._ [More...](#detailed-description)

* `#include <stdint.h>`
* `#include <stdbool.h>`
* `#include <stddef.h>`
* `#include <string.h>`
* `#include "sl_status.h"`
* `#include "cmsis_os2.h"`
* `#include "config.h"`
* `#include "log.h"`
* `#include "led.h"`





































## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**common\_init**](#function-common_init) (void) <br>_Initialize some common stuff._  |
|  void | [**common\_tick\_update**](#function-common_tick_update) (void) <br>_Update the common tick._  |
|  uint32\_t | [**core\_clock\_hz**](#function-core_clock_hz) (void) <br>_Get the current core clock in Hz._  |
|  void | [**delay\_ms**](#function-delay_ms) (uint32\_t ms) <br>_Delay for a given number of milliseconds._  |
|  void | [**delay\_ns**](#function-delay_ns) (uint64\_t ns) <br>_Delay for a given number of nanoseconds._  |
|  sl\_status\_t | [**log\_status**](#function-log_status) (const char \* file, int line, sl\_status\_t status) <br>_Log an error message with file and line information._  |
|  uint32\_t | [**time\_ms**](#function-time_ms) (void) <br>_Get the current time in milliseconds._  |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**CONCAT\_2**](common_8h.md#define-concat_2) (a, b) `a##b`<br>_Concatenate two tokens._  |
| define  | [**CONCAT\_3**](common_8h.md#define-concat_3) (a, b, c) `a##b##c`<br>_Concatenate three tokens._  |
| define  | [**LOG\_RET\_STATUS**](common_8h.md#define-log_ret_status) (x) `/* multi line expression */`<br>_Macro to check the status of a function call and return if it is not_ `SL_STATUS_OK` __ |
| define  | [**LOG\_RET\_VOID**](common_8h.md#define-log_ret_void) (x) `/* multi line expression */`<br>_Macro to check the status of a function call and return if it is not_ `SL_STATUS_OK` __ |
| define  | [**LOG\_STATUS**](common_8h.md#define-log_status) (status) `[**log\_status**](common_8h.md#function-log_status)(\_\_FILE\_\_, \_\_LINE\_\_, (status))`<br>_Macro to log the status of a function call with file and line information._  |
| define  | [**TICKS\_PER\_SEC**](common_8h.md#define-ticks_per_sec)  `(OS\_Tick\_GetClock() / OS\_Tick\_GetInterval())`<br>_Number of RTOS ticks per second._  |
| define  | [**UNUSED**](common_8h.md#define-unused) (x) `(void)(x)`<br>_Suppress unused variable warning._  |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Functions Documentation




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
## Macro Definition Documentation





### define CONCAT\_2 

_Concatenate two tokens._ 
```C++
#define CONCAT_2 (
    a,
    b
) `a##b`
```




<hr>



### define CONCAT\_3 

_Concatenate three tokens._ 
```C++
#define CONCAT_3 (
    a,
    b,
    c
) `a##b##c`
```




<hr>



### define LOG\_RET\_STATUS 

_Macro to check the status of a function call and return if it is not_ `SL_STATUS_OK` __
```C++
#define LOG_RET_STATUS (
    x
) `/* multi line expression */`
```





**Parameters:**


* `x` Function call to check



**Warning:**

This macro returns with `sl_status_t` 




        

<hr>



### define LOG\_RET\_VOID 

_Macro to check the status of a function call and return if it is not_ `SL_STATUS_OK` __
```C++
#define LOG_RET_VOID (
    x
) `/* multi line expression */`
```





**Parameters:**


* `x` Function call to check



**Warning:**

This macro returns with `void` 




        

<hr>



### define LOG\_STATUS 

_Macro to log the status of a function call with file and line information._ 
```C++
#define LOG_STATUS (
    status
) `log_status (__FILE__, __LINE__, (status))`
```





**Parameters:**


* `status` Status to log 



        

<hr>



### define TICKS\_PER\_SEC 

_Number of RTOS ticks per second._ 
```C++
#define TICKS_PER_SEC `(OS_Tick_GetClock() / OS_Tick_GetInterval())`
```




<hr>



### define UNUSED 

_Suppress unused variable warning._ 
```C++
#define UNUSED (
    x
) `(void)(x)`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/common/common.h`

