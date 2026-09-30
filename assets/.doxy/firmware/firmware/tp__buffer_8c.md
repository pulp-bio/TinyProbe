

# File tp\_buffer.c



[**FileList**](files.md) **>** [**common**](dir_b3d49238ee93ee123788c1fa6c06a286.md) **>** [**tp\_buffer.c**](tp__buffer_8c.md)

[Go to the source code of this file](tp__buffer_8c_source.md)

_TinyProbe buffer handler source file._ [More...](#detailed-description)

* `#include "tp_buffer.h"`

















## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**buffer\_history\_event**](#enum-buffer_history_event)  <br> |
| typedef enum buffer\_history\_event | [**buffer\_history\_event\_t**](#typedef-buffer_history_event_t)  <br> |




















## Public Functions

| Type | Name |
| ---: | :--- |
|  [**tp\_buffer\_slot\_t**](structtp__buffer__slot__t.md) \* | [**tp\_buffer\_claim\_reading**](#function-tp_buffer_claim_reading) ([**tp\_buffer\_t**](structtp__buffer__t.md) \* buf) <br>_Return a buffer slot after writing._  |
|  [**tp\_buffer\_slot\_t**](structtp__buffer__slot__t.md) \* | [**tp\_buffer\_claim\_writing**](#function-tp_buffer_claim_writing) ([**tp\_buffer\_t**](structtp__buffer__t.md) \* buf) <br>_Claim a buffer slot for writing._  |
|  size\_t | [**tp\_buffer\_history\_get**](#function-tp_buffer_history_get) (uint32\_t \*\* history) <br>_Get the buffer history._  |
|  void | [**tp\_buffer\_history\_reset**](#function-tp_buffer_history_reset) (void) <br>_Reset the buffer history._  |
|  sl\_status\_t | [**tp\_buffer\_init**](#function-tp_buffer_init) ([**tp\_buffer\_t**](structtp__buffer__t.md) \* buf) <br>_Initialize the buffer structure._  |
|  void | [**tp\_buffer\_return\_reading**](#function-tp_buffer_return_reading) ([**tp\_buffer\_t**](structtp__buffer__t.md) \* buf, [**tp\_buffer\_slot\_t**](structtp__buffer__slot__t.md) \* slot) <br>_Return a buffer slot after reading._  |
|  void | [**tp\_buffer\_return\_writing**](#function-tp_buffer_return_writing) ([**tp\_buffer\_t**](structtp__buffer__t.md) \* buf, [**tp\_buffer\_slot\_t**](structtp__buffer__slot__t.md) \* slot) <br>_Return a buffer slot after writing._  |


## Public Static Functions

| Type | Name |
| ---: | :--- |
|  void | [**buffer\_history\_record**](#function-buffer_history_record) (buffer\_history\_event\_t event, uint8\_t buffer\_index) <br> |


























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Types Documentation




### enum buffer\_history\_event 

```C++
enum buffer_history_event {
    BUFFER_HISTORY_EVENT_CLAIM_WRITE = 0,
    BUFFER_HISTORY_EVENT_RETURN_WRITE = 1,
    BUFFER_HISTORY_EVENT_CLAIM_READ = 2,
    BUFFER_HISTORY_EVENT_RETURN_READ = 3
};
```




<hr>



### typedef buffer\_history\_event\_t 

```C++
typedef enum buffer_history_event  buffer_history_event_t;
```




<hr>
## Public Functions Documentation




### function tp\_buffer\_claim\_reading 

_Return a buffer slot after writing._ 
```C++
tp_buffer_slot_t * tp_buffer_claim_reading (
    tp_buffer_t * buf
) 
```





**Parameters:**


* `buf` Buffer structure to return to



**Returns:**

Pointer to the claimed buffer slot 




        

<hr>



### function tp\_buffer\_claim\_writing 

_Claim a buffer slot for writing._ 
```C++
tp_buffer_slot_t * tp_buffer_claim_writing (
    tp_buffer_t * buf
) 
```





**Parameters:**


* `buf` Buffer structure to claim from



**Returns:**

Pointer to the claimed buffer slot 




        

<hr>



### function tp\_buffer\_history\_get 

_Get the buffer history._ 
```C++
size_t tp_buffer_history_get (
    uint32_t ** history
) 
```





**Parameters:**


* `history` Pointer to the history array



**Returns:**

size\_t Number of entries in the history




**Warning:**

The history is only available if TP\_BUFFER\_HISTORY is enabled, otherwise history will be NULL and size 0 




        

<hr>



### function tp\_buffer\_history\_reset 

_Reset the buffer history._ 
```C++
void tp_buffer_history_reset (
    void
) 
```




<hr>



### function tp\_buffer\_init 

_Initialize the buffer structure._ 
```C++
sl_status_t tp_buffer_init (
    tp_buffer_t * buf
) 
```





**Parameters:**


* `buf` Buffer structure to initialize 



        

<hr>



### function tp\_buffer\_return\_reading 

_Return a buffer slot after reading._ 
```C++
void tp_buffer_return_reading (
    tp_buffer_t * buf,
    tp_buffer_slot_t * slot
) 
```





**Parameters:**


* `buf` Buffer structure to return to 
* `slot` Pointer to the buffer slot to return 



        

<hr>



### function tp\_buffer\_return\_writing 

_Return a buffer slot after writing._ 
```C++
void tp_buffer_return_writing (
    tp_buffer_t * buf,
    tp_buffer_slot_t * slot
) 
```





**Parameters:**


* `buf` Buffer structure to return to 
* `slot` Pointer to the buffer slot to return 



        

<hr>
## Public Static Functions Documentation




### function buffer\_history\_record 

```C++
static inline void buffer_history_record (
    buffer_history_event_t event,
    uint8_t buffer_index
) 
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/common/tp_buffer.c`

