

# Struct wius\_spi\_inst



[**ClassList**](annotated.md) **>** [**wius\_spi\_inst**](structwius__spi__inst.md)



_SPI instance enumeration._ 

* `#include <wius_spi.h>`

















## Public Types

| Type | Name |
| ---: | :--- |
| union  | [**instance**](#union-instance)  <br> |




## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**wius\_spi\_config\_t**](wius__spi_8h.md#typedef-wius_spi_config_t) | [**config**](#variable-config)  <br> |
|  [**wius\_gpio\_t**](wius__gpio_8h.md#typedef-wius_gpio_t) | [**cs**](#variable-cs)  <br> |
|  uint8\_t | [**id**](#variable-id)  <br> |
|  union [**wius\_spi\_inst::instance**](unionwius__spi__inst_1_1instance.md) | [**inst**](#variable-inst)  <br> |












































## Public Types Documentation




### union instance 

```C++

```



&lt; Peripheral handle union 

    

<hr>
## Public Attributes Documentation




### variable config 

```C++
wius_spi_config_t wius_spi_inst::config;
```



Configuration 

        

<hr>



### variable cs 

```C++
wius_gpio_t wius_spi_inst::cs;
```



Chip select GPIO (only in SW/HW mode) 

        

<hr>



### variable id 

```C++
uint8_t wius_spi_inst::id;
```



Instance ID 

        

<hr>



### variable inst 

```C++
union wius_spi_inst::instance  wius_spi_inst::inst;
```



Peripheral handle 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_spi.h`

