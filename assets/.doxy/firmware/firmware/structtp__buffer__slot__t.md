

# Struct tp\_buffer\_slot\_t



[**ClassList**](annotated.md) **>** [**tp\_buffer\_slot\_t**](structtp__buffer__slot__t.md)



_Buffer slot structure._ 

* `#include <tp_buffer.h>`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  uint8\_t | [**data**](#variable-data)  <br> |
|  size\_t | [**id**](#variable-id)  <br> |
|  size\_t | [**length**](#variable-length)  <br> |
|  [**tp\_buffer\_status\_t**](tp__buffer_8h.md#enum-tp_buffer_status_t) | [**status**](#variable-status)  <br> |












































## Public Attributes Documentation




### variable data 

```C++
uint8_t tp_buffer_slot_t::data[TP_BUFFER_SIZE];
```



Buffer data 

        

<hr>



### variable id 

```C++
size_t tp_buffer_slot_t::id;
```



ID of the slot 

        

<hr>



### variable length 

```C++
size_t tp_buffer_slot_t::length;
```



Length of the buffer data 

        

<hr>



### variable status 

```C++
tp_buffer_status_t tp_buffer_slot_t::status;
```



Status of the buffer 

**Warning:**

Do not modify 




        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/common/tp_buffer.h`

