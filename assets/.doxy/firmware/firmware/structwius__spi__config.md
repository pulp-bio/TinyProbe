

# Struct wius\_spi\_config



[**ClassList**](annotated.md) **>** [**wius\_spi\_config**](structwius__spi__config.md)



_SPI instance configuration._ 

* `#include <wius_spi.h>`





















## Public Attributes

| Type | Name |
| ---: | :--- |
|  [**wius\_spi\_cs\_mode\_t**](wius__spi_8h.md#typedef-wius_spi_cs_mode_t) | [**cs\_mode**](#variable-cs_mode)  <br> |
|  uint8\_t | [**cs\_pin**](#variable-cs_pin)  <br> |
|  uint8\_t | [**cs\_polarity**](#variable-cs_polarity)  <br> |
|  uint32\_t | [**freq**](#variable-freq)  <br> |
|  uint8\_t | [**mode**](#variable-mode)  <br> |
|  uint8\_t | [**width**](#variable-width)  <br> |












































## Public Attributes Documentation




### variable cs\_mode 

```C++
wius_spi_cs_mode_t wius_spi_config::cs_mode;
```



Chip select mode 

        

<hr>



### variable cs\_pin 

```C++
uint8_t wius_spi_config::cs_pin;
```



Chip select pin (only for SW mode) 

        

<hr>



### variable cs\_polarity 

```C++
uint8_t wius_spi_config::cs_polarity;
```



Chip select polarity (only for SW mode, 0 for active low, 1 for active high) 

        

<hr>



### variable freq 

```C++
uint32_t wius_spi_config::freq;
```



Clock frequency in Hz 

        

<hr>



### variable mode 

```C++
uint8_t wius_spi_config::mode;
```



SPI mode (0-3) 

        

<hr>



### variable width 

```C++
uint8_t wius_spi_config::width;
```



Data width in bits 

        

<hr>

------------------------------
The documentation for this class was generated from the following file `firmware/user/wius/hal/wius_spi.h`

