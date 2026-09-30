

# File log.h



[**FileList**](files.md) **>** [**common**](dir_85edcc1f099af2a701a791767791d401.md) **>** [**log.h**](log_8h.md)

[Go to the source code of this file](log_8h_source.md)

_Logging header file._ [More...](#detailed-description)

* `#include <stdarg.h>`
* `#include <stdbool.h>`

















## Public Types

| Type | Name |
| ---: | :--- |
| typedef int(\* | [**log\_callback\_t**](#typedef-log_callback_t)  <br> |
| enum  | [**log\_level\_e**](#enum-log_level_e)  <br> |
| typedef enum log\_level\_e | [**log\_level\_t**](#typedef-log_level_t)  <br> |




## Public Attributes

| Type | Name |
| ---: | :--- |
|  const char \* | [**log\_level\_strings**](#variable-log_level_strings)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**log\_log**](#function-log_log) (log\_level\_t level, const char \* file, const char \* function, int line, const char \* fmt, ...) <br> |
|  bool | [**log\_register\_callback**](#function-log_register_callback) (log\_callback\_t callback) <br> |
|  bool | [**log\_unregister\_callback**](#function-log_unregister_callback) (log\_callback\_t callback) <br> |



























## Macros

| Type | Name |
| ---: | :--- |
| define  | [**LOG\_BUFFER\_SIZE**](log_8h.md#define-log_buffer_size)  `128`<br> |
| define  | [**LOG\_MAX\_CALLBACKS**](log_8h.md#define-log_max_callbacks)  `2`<br> |
| define  | [**\_LOG\_LOG**](log_8h.md#define-_log_log) (level, fmt, ...) `log\_log(level, \_\_FILE\_NAME\_\_, \_\_FUNCTION\_\_, \_\_LINE\_\_, fmt, ##\_\_VA\_ARGS\_\_)`<br> |
| define  | [**log\_debug**](log_8h.md#define-log_debug) (fmt, ...) `\_LOG\_LOG(DEBUG, fmt, ##\_\_VA\_ARGS\_\_)`<br> |
| define  | [**log\_error**](log_8h.md#define-log_error) (fmt, ...) `\_LOG\_LOG(ERROR, fmt, ##\_\_VA\_ARGS\_\_)`<br> |
| define  | [**log\_fatal**](log_8h.md#define-log_fatal) (fmt, ...) `\_LOG\_LOG(FATAL, fmt, ##\_\_VA\_ARGS\_\_)`<br> |
| define  | [**log\_info**](log_8h.md#define-log_info) (fmt, ...) `\_LOG\_LOG(INFO, fmt, ##\_\_VA\_ARGS\_\_)`<br> |
| define  | [**log\_trace**](log_8h.md#define-log_trace) (fmt, ...) `\_LOG\_LOG(TRACE, fmt, ##\_\_VA\_ARGS\_\_)`<br> |
| define  | [**log\_warn**](log_8h.md#define-log_warn) (fmt, ...) `\_LOG\_LOG(WARN, fmt, ##\_\_VA\_ARGS\_\_)`<br> |

## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### typedef log\_callback\_t 

```C++
typedef int(* log_callback_t) (const char *str, int len);
```




<hr>



### enum log\_level\_e 

```C++
enum log_level_e {
    TRACE = 0,
    DEBUG = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
    FATAL = 5,
    LOG_LEVEL_COUNT
};
```




<hr>



### typedef log\_level\_t 

```C++
typedef enum log_level_e  log_level_t;
```




<hr>
## Public Attributes Documentation




### variable log\_level\_strings 

```C++
const char* log_level_strings[LOG_LEVEL_COUNT];
```




<hr>
## Public Functions Documentation




### function log\_log 

```C++
void log_log (
    log_level_t level,
    const char * file,
    const char * function,
    int line,
    const char * fmt,
    ...
) 
```




<hr>



### function log\_register\_callback 

```C++
bool log_register_callback (
    log_callback_t callback
) 
```




<hr>



### function log\_unregister\_callback 

```C++
bool log_unregister_callback (
    log_callback_t callback
) 
```




<hr>
## Macro Definition Documentation





### define LOG\_BUFFER\_SIZE 

```C++
#define LOG_BUFFER_SIZE `128`
```




<hr>



### define LOG\_MAX\_CALLBACKS 

```C++
#define LOG_MAX_CALLBACKS `2`
```




<hr>



### define \_LOG\_LOG 

```C++
#define _LOG_LOG (
    level,
    fmt,
    ...
) `log_log(level, __FILE_NAME__, __FUNCTION__, __LINE__, fmt, ##__VA_ARGS__)`
```




<hr>



### define log\_debug 

```C++
#define log_debug (
    fmt,
    ...
) `_LOG_LOG(DEBUG, fmt, ##__VA_ARGS__)`
```




<hr>



### define log\_error 

```C++
#define log_error (
    fmt,
    ...
) `_LOG_LOG(ERROR, fmt, ##__VA_ARGS__)`
```




<hr>



### define log\_fatal 

```C++
#define log_fatal (
    fmt,
    ...
) `_LOG_LOG(FATAL, fmt, ##__VA_ARGS__)`
```




<hr>



### define log\_info 

```C++
#define log_info (
    fmt,
    ...
) `_LOG_LOG(INFO, fmt, ##__VA_ARGS__)`
```




<hr>



### define log\_trace 

```C++
#define log_trace (
    fmt,
    ...
) `_LOG_LOG(TRACE, fmt, ##__VA_ARGS__)`
```




<hr>



### define log\_warn 

```C++
#define log_warn (
    fmt,
    ...
) `_LOG_LOG(WARN, fmt, ##__VA_ARGS__)`
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/common/log.h`

