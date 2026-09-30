

# Struct tp\_buffer\_t



[**ClassList**](annotated.md) **>** [**tp\_buffer\_t**](structtp__buffer__t.md)



_Buffer structure._ [More...](#detailed-description)

* `#include <tp_buffer.h>`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  size\_t | [**head**](#variable-head)  <br> |
|  osSemaphoreId\_t | [**sem\_read**](#variable-sem_read)  <br> |
|  osSemaphoreId\_t | [**sem\_write**](#variable-sem_write)  <br> |
|  [**tp\_buffer\_slot\_t**](structtp__buffer__slot__t.md) | [**slots**](#variable-slots)  <br> |
|  size\_t | [**tail**](#variable-tail)  <br> |












































## Detailed Description




**Warning:**

Do not modify the structure directly 




    
## Public Attributes Documentation




### variable head 

```C++
size_t tp_buffer_t::head;
```



Head index 

        

<hr>



### variable sem\_read 

```C++
osSemaphoreId_t tp_buffer_t::sem_read;
```



Semaphore for reading 

        

<hr>



### variable sem\_write 

```C++
osSemaphoreId_t tp_buffer_t::sem_write;
```



Semaphore for writing 

        

<hr>



### variable slots 

```C++
tp_buffer_slot_t tp_buffer_t::slots[TP_BUFFER_NUM];
```



Buffer slots 

        

<hr>



### variable tail 

```C++
size_t tp_buffer_t::tail;
```



Tail index 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/tp/common/tp_buffer.h`

