

# Group config\_common



[**Modules**](modules.md) **>** [**config\_common**](group__config__common.md)



[More...](#detailed-description)

































































## Macros

| Type | Name |
| ---: | :--- |
| define  | [**LOG\_BUFFER\_SIZE**](config_8h.md#define-log_buffer_size)  `128`<br>_Remove lifetime of log library (no deinitialization, no callback unregistration)_  |
| define  | [**LOG\_MAX\_CALLBACKS**](config_8h.md#define-log_max_callbacks)  `1`<br>_&lt; Maximum number of log callbacks that can be registered_  |
| define  | [**LOG\_NO\_COLOR**](config_8h.md#define-log_no_color)  <br> |
| define  | [**LOG\_ONCE**](config_8h.md#define-log_once)  <br> |
| define  | [**WIUS\_BOARD**](config_8h.md#define-wius_board)  `3`<br>_&lt; Board type for WiUS firmware. Can be one of 0: "DK2605A", 1: "EK2708A", 2: "PK6031A", 3: "WIUS1"._  |

## Detailed Description


This module documents the common firmware configurations. 

    
## Macro Definition Documentation





### define LOG\_BUFFER\_SIZE 

_Remove lifetime of log library (no deinitialization, no callback unregistration)_ 
```C++
#define LOG_BUFFER_SIZE `128`
```




<hr>



### define LOG\_MAX\_CALLBACKS 

_&lt; Maximum number of log callbacks that can be registered_ 
```C++
#define LOG_MAX_CALLBACKS `1`
```



Size of the log buffer in bytes 

        

<hr>



### define LOG\_NO\_COLOR 

```C++
#define LOG_NO_COLOR 
```




<hr>



### define LOG\_ONCE 

```C++
#define LOG_ONCE 
```




<hr>



### define WIUS\_BOARD 

_&lt; Board type for WiUS firmware. Can be one of 0: "DK2605A", 1: "EK2708A", 2: "PK6031A", 3: "WIUS1"._ 
```C++
#define WIUS_BOARD `3`
```




<hr>

------------------------------


