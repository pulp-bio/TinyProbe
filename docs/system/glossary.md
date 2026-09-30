# Glossary And Contributor Orientation

## Glossary

| Term | Meaning |
| --- | --- |
| AFE | Analog front end. In TinyProbe this is the AFE5832LP receive chip. |
| Acquisition | One configured run that may contain one or more ultrasound shots and RF data transfers. |
| Capture delay | Delay from the FPGA trigger point to the start of FIFO capture. |
| FIFO | First-in, first-out buffer in the FPGA used to hold captured RF samples until MCU readout. |
| FPGA | Field-programmable gate array. Generates timing, captures LVDS data, and buffers samples. |
| Gateware | The SystemVerilog design programmed into the FPGA. |
| Host | The PC running the `tipy` Python package. It configures acquisitions and receives data. |
| LVDS | Differential digital interface used by the AFE to send receive sample data and clocks to the FPGA. |
| MCU | Microcontroller on the Wi-Fi board. It owns Wi-Fi, SPI target selection, power GPIOs, and command handling. |
| Power domain | A controllable board supply such as positive HV, negative HV, negative 5 V, or LVDS 2.5 V. |
| Shot | One transmit/receive event inside an acquisition. |
| Sync period | FPGA waveform-generator period between trigger opportunities. |
| TGC | Time gain compensation. A gain ramp applied during receive to compensate depth-dependent attenuation. |
| TX BF | Transmit beamformer. In TinyProbe this refers to TX7332 timing and pulse control. |
