

# Group wius



[**Modules**](modules.md) **>** [**wius**](group__wius.md)



_Wireless transport, sockets, and power coordination for TinyProbe._ [More...](#detailed-description)








## Files

| Type | Name |
| ---: | :--- |
| file | [**wius\_gpio.c**](wius__gpio_8c.md) <br>_WiUS GPIO implementation source file._  |
| file | [**wius\_gpio.h**](wius__gpio_8h.md) <br>_WiUS GPIO implementation header file._  |
| file | [**wius\_power.c**](wius__power_8c.md) <br>_WiUS power management source file._  |
| file | [**wius\_power.h**](wius__power_8h.md) <br>_WiUS power management header file._  |
| file | [**wius\_spi.c**](wius__spi_8c.md) <br>_WiUS SPI implementation source file._  |
| file | [**wius\_spi.h**](wius__spi_8h.md) <br>_WiUS SPI implementation header file._  |
| file | [**wius\_tcp.c**](wius__tcp_8c.md) <br>_WiUS TCP implementation source file._  |
| file | [**wius\_tcp.h**](wius__tcp_8h.md) <br>_WiUS TCP implementation header file._  |
| file | [**wius\_udp.c**](wius__udp_8c.md) <br>_WiUS UDP implementation source file._  |
| file | [**wius\_udp.h**](wius__udp_8h.md) <br>_WiUS UDP implementation header file._  |
| file | [**wius\_wifi.c**](wius__wifi_8c.md) <br>_WiUS WiFi implementation source file._  |
| file | [**wius\_wifi.h**](wius__wifi_8h.md) <br>_WiUS WiFi implementation header file._  |




## Modules

| Type | Name |
| ---: | :--- |
| module | [**WiUS firmware configurations**](group__config__wius.md) <br> |






















































## Detailed Description


# WiUS Module




The WiUS module handles connectivity, sockets, and power states for the probe. It exposes TCP/UDP helpers that feed TinyProbe's command pipeline and provides GPIO/SPI abstractions used by the hardware-facing code.

## Responsibilities





* Networking: TCP server and UDP helpers in [**wius\_tcp.h**](wius__tcp_8h.md) and [**wius\_udp.h**](wius__udp_8h.md)
* Wi-Fi control: initialization and mDNS helpers in [**wius\_wifi.h**](wius__wifi_8h.md)
* Peripheral access: GPIO and SPI wrappers in [**wius\_gpio.h**](wius__gpio_8h.md) and [**wius\_spi.h**](wius__spi_8h.md)
* Power: power mode helpers in [**wius\_power.h**](wius__power_8h.md)



## Interaction with TinyProbe





* Incoming network packets are delivered to the [**TinyProbe**](group__tinyprobe.md) dispatcher along with metadata required for replies.
* Command replies (when enabled) are sent back via WiUS TCP/UDP primitives.
* Power state transitions should be coordinated so that active transfers are drained before entering low-power modes.



## Notes for Contributors





* Keep socket buffer sizes and queue depths in sync with command expectations to avoid partial frames.
* When adding transports or altering power behavior, document the flow here and cross-reference the affected command handlers. 



    

------------------------------


