@defgroup wius WiUS Module
@brief Wireless transport, sockets, and power coordination for TinyProbe

# WiUS Module

The WiUS module handles connectivity, sockets, and power states for the probe. It exposes TCP/UDP helpers that feed TinyProbe's command pipeline and provides GPIO/SPI abstractions used by the hardware-facing code.

## Responsibilities
- Networking: TCP server and UDP helpers in [wius_tcp.h](wius_tcp.h) and [wius_udp.h](wius_udp.h)
- Wi-Fi control: initialization and mDNS helpers in [wius_wifi.h](wius_wifi.h)
- Peripheral access: GPIO and SPI wrappers in [wius_gpio.h](wius_gpio.h) and [wius_spi.h](wius_spi.h)
- Power: power mode helpers in [wius_power.h](wius_power.h)

## Interaction with TinyProbe
- Incoming network packets are delivered to the [TinyProbe](../tp/module.md) dispatcher along with metadata required for replies.
- Command replies (when enabled) are sent back via WiUS TCP/UDP primitives.
- Power state transitions should be coordinated so that active transfers are drained before entering low-power modes.

## Notes for Contributors
- Keep socket buffer sizes and queue depths in sync with command expectations to avoid partial frames.
- When adding transports or altering power behavior, document the flow here and cross-reference the affected command handlers.

@addtogroup wius
@{
@}