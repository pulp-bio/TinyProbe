

# File user.c



[**FileList**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**user.c**](user_8c.md)

[Go to the source code of this file](user_8c_source.md)

_User main source file._ [More...](#detailed-description)

* `#include "user.h"`
* `#include <stdio.h>`
* `#include "common.h"`
* `#include "tp.h"`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  const osThreadAttr\_t | [**user\_application\_attr**](#variable-user_application_attr)   = `/* multi line expression */`<br> |
|  osThreadId\_t | [**user\_application\_id**](#variable-user_application_id)  <br> |
















## Public Functions

| Type | Name |
| ---: | :--- |
|  void | [**user\_init**](#function-user_init) (void) <br>_Initialize the user application._  |


## Public Static Functions

| Type | Name |
| ---: | :--- |
|  void | [**user\_application**](#function-user_application) (void \* argument) <br> |


























## Detailed Description




**Date:**

03.09.2026 




**Copyright:**

Copyright (C) 2026 ETH Zurich. All rights reserved.




**Author:**

Cédric Hirschi, ETH Zürich




    
## Public Attributes Documentation




### variable user\_application\_attr 

```C++
const osThreadAttr_t user_application_attr;
```




<hr>



### variable user\_application\_id 

```C++
osThreadId_t user_application_id;
```




<hr>
## Public Functions Documentation




### function user\_init 

_Initialize the user application._ 
```C++
void user_init (
    void
) 
```





**Note:**

This function should create the user application thread as well 




        

<hr>
## Public Static Functions Documentation




### function user\_application 

```C++
static void user_application (
    void * argument
) 
```




<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/user.c`

