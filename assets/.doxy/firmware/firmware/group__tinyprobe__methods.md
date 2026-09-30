

# Group tinyprobe\_methods



[**Modules**](modules.md) **>** [**tinyprobe\_methods**](group__tinyprobe__methods.md)



_Method handlers for TinyProbe control operations._ [More...](#detailed-description)








## Files

| Type | Name |
| ---: | :--- |
| file | [**tp\_method\_controlpower.c**](tp__method__controlpower_8c.md) <br>_TinyProbe control power method implementation file._  |
| file | [**tp\_method\_controlpower.h**](tp__method__controlpower_8h.md) <br>_TinyProbe control power method header file._  |
| file | [**tp\_method\_controlspi.c**](tp__method__controlspi_8c.md) <br>_TinyProbe SPI control method implementation file._  |
| file | [**tp\_method\_controlspi.h**](tp__method__controlspi_8h.md) <br>_TinyProbe SPI control method header file._  |
| file | [**tp\_method\_delayms.c**](tp__method__delayms_8c.md) <br>_TinyProbe delay in milliseconds method implementation file._  |
| file | [**tp\_method\_delayms.h**](tp__method__delayms_8h.md) <br>_TinyProbe delay in milliseconds method header file._  |
| file | [**tp\_method\_delayns.c**](tp__method__delayns_8c.md) <br>_TinyProbe delay in nanoseconds method implementation file._  |
| file | [**tp\_method\_delayns.h**](tp__method__delayns_8h.md) <br>_TinyProbe delay in nanoseconds method header file._  |
| file | [**tp\_method\_ping.c**](tp__method__ping_8c.md) <br>_TinyProbe ping method implementation file._  |
| file | [**tp\_method\_ping.h**](tp__method__ping_8h.md) <br>_TinyProbe ping method header file._  |
| file | [**tp\_method\_setloglevel.c**](tp__method__setloglevel_8c.md) <br>_TinyProbe set log level method implementation file._  |
| file | [**tp\_method\_setloglevel.h**](tp__method__setloglevel_8h.md) <br>_TinyProbe set log level method header file._  |
| file | [**tp\_method\_triggershot.c**](tp__method__triggershot_8c.md) <br>_TinyProbe Trigger Shot method implementation file._  |
| file | [**tp\_method\_triggershot.h**](tp__method__triggershot_8h.md) <br>_TinyProbe Trigger Shot method header file._  |
| file | [**tp\_method\_writeafe.c**](tp__method__writeafe_8c.md) <br>_TinyProbe AFE write method implementation file._  |
| file | [**tp\_method\_writeafe.h**](tp__method__writeafe_8h.md) <br>_TinyProbe AFE write method header file._  |
| file | [**tp\_method\_writefpga.c**](tp__method__writefpga_8c.md) <br>_TinyProbe FPGA write method implementation file._  |
| file | [**tp\_method\_writefpga.h**](tp__method__writefpga_8h.md) <br>_TinyProbe FPGA write method header file._  |
| file | [**tp\_method\_writetx.c**](tp__method__writetx_8c.md) <br>_TinyProbe TX write method implementation file._  |
| file | [**tp\_method\_writetx.h**](tp__method__writetx_8h.md) <br>_TinyProbe TX write method header file._  |


























































## Detailed Description


# TinyProbe Methods




This group contains all method handlers used by TinyProbe to interact with hardware and system services. Each method implementation and its public interface lives in this subgroup to keep the method surface easy to navigate.

## Method Catalog





|Method  |Header  |Description   |
|-----|-----|-----|
|Ping  |[**tp\_method\_ping.h**](tp__method__ping_8h.md)  |Reachability and identity check   |
|Trigger shot  |[**tp\_method\_triggershot.h**](tp__method__triggershot_8h.md)  |Trigger capture   |
|Delay ns  |[**tp\_method\_delayns.h**](tp__method__delayns_8h.md)  |Nanosecond timing control   |
|Delay ms  |[**tp\_method\_delayms.h**](tp__method__delayms_8h.md)  |Millisecond timing control   |
|Power control  |[**tp\_method\_controlpower.h**](tp__method__controlpower_8h.md)  |Toggle power rails   |
|Set log level  |[**tp\_method\_setloglevel.h**](tp__method__setloglevel_8h.md)  |Configure firmware log verbosity   |
|SPI MUX  |[**tp\_method\_controlspi.h**](tp__method__controlspi_8h.md)  |Select SPI MUX target   |
|Write AFE  |[**tp\_method\_writeafe.h**](tp__method__writeafe_8h.md)  |AFE register write   |
|Write FPGA  |[**tp\_method\_writefpga.h**](tp__method__writefpga_8h.md)  |FPGA register write   |
|Write TX  |[**tp\_method\_writetx.h**](tp__method__writetx_8h.md)  |TX buffer write   |





## How Methods Are Dispatched





* Incoming framed protobuf packets are decoded by `tp_methods_handle()` in [**tp\_methods.h**](tp__methods_8h.md).
* The dispatcher switches on the generated nanopb oneof tag and calls the corresponding handler from this group.
* Handlers validate arguments, perform hardware actions through [**common**](group__common.md) helpers and TinyProbe drivers, and return a generated status code.



## Adding a New Method





* Create `tp_method_<name>.c/.h` under `user/tp/methods/`.
* Add it to the generated method definition and include it in the `TP_METHODS` macro.
* Document it in this catalog and keep the description concise (what it does, inputs, side effects). 



    

------------------------------


