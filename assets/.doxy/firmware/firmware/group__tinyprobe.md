

# Group tinyprobe



[**Modules**](modules.md) **>** [**tinyprobe**](group__tinyprobe.md)



_Method processing, FPGA/AFE control, and probe orchestration._ [More...](#detailed-description)








## Files

| Type | Name |
| ---: | :--- |
| file | [**tp.c**](tp_8c.md) <br>_TinyProbe main source file._  |
| file | [**tp.h**](tp_8h.md) <br>_TinyProbe main header file._  |
| file | [**tp\_afe.c**](tp__afe_8c.md) <br>_TinyProbe AFE driver source file._  |
| file | [**tp\_afe.h**](tp__afe_8h.md) <br>_TinyProbe AFE driver header file._  |
| file | [**tp\_buffer.c**](tp__buffer_8c.md) <br>_TinyProbe buffer handler source file._  |
| file | [**tp\_buffer.h**](tp__buffer_8h.md) <br>_TinyProbe buffer handler header file._  |
| file | [**tp\_fpga.c**](tp__fpga_8c.md) <br>_TinyProbe FPGA driver source file._  |
| file | [**tp\_fpga.h**](tp__fpga_8h.md) <br>_TinyProbe FPGA driver header file._  |
| file | [**tp\_methods.c**](tp__methods_8c.md) <br>_TinyProbe methods implementation file._  |
| file | [**tp\_methods.h**](tp__methods_8h.md) <br>_TinyProbe methods header file._  |
| file | [**tp\_mux.c**](tp__mux_8c.md) <br>_TinyProbe SPI MUX driver source file._  |
| file | [**tp\_mux.h**](tp__mux_8h.md) <br>_TinyProbe SPI MUX driver header file._  |
| file | [**tp\_power.c**](tp__power_8c.md) <br>_TinyProbe power management driver source file._  |
| file | [**tp\_power.h**](tp__power_8h.md) <br>_TinyProbe power management driver header file._  |
| file | [**tp\_tx.c**](tp__tx_8c.md) <br>_TinyProbe TX chip driver source file._  |
| file | [**tp\_tx.h**](tp__tx_8h.md) <br>_TinyProbe TX chip driver header file._  |




## Modules

| Type | Name |
| ---: | :--- |
| module | [**TinyProbe firmware configurations**](group__config__tinyprobe.md) <br> |
| module | [**TinyProbe Methods**](group__tinyprobe__methods.md) <br>_Method handlers for TinyProbe control operations._  |






















































## Detailed Description


# TinyProbe Module




TinyProbe translates incoming control messages into hardware actions on the probe. It owns the method registry, FPGA/AFE access, and buffers that feed outbound data paths.

## Architecture





* Method dispatch: protobuf request decoding and routing in [**tp\_methods.h**](tp__methods_8h.md)
* Method handlers: grouped under [**TinyProbe Methods**](group__tinyprobe__methods.md) with one handler per generated method
* Hardware control: FPGA, AFE, TX, mux, and power accessors in [**tp\_fpga.h**](tp__fpga_8h.md), [**tp\_afe.h**](tp__afe_8h.md), [**tp\_tx.h**](tp__tx_8h.md), [**tp\_mux.h**](tp__mux_8h.md), and [**tp\_power.h**](tp__power_8h.md)
* Buffering: circular buffer helpers in [**tp\_buffer.h**](tp__buffer_8h.md)



## Data Flow (high level)





* WiUS transport receives a message and forwards it to the TinyProbe method layer.
* `tp_methods_handle()` decodes the nanopb request and selects the matching handler from [**TinyProbe Methods**](group__tinyprobe__methods.md).
* Handlers perform register writes/reads through TinyProbe helpers and may enqueue data into probe buffers.
* Status replies are encoded as protobuf responses and returned via the WiUS transport.



## Extending TinyProbe





* Add a new method: update the generated method definition, create `tp_method_<name>.c/.h`, add it to `TP_METHODS`, and document it under [**TinyProbe Methods**](group__tinyprobe__methods.md).
* Touch hardware safely: prefer helper APIs in `tp_fpga`, `tp_afe`, `tp_tx`, `tp_mux`, and `tp_power` rather than open-coded register writes to keep side effects contained. 



    

------------------------------


