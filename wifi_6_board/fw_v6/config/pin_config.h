#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

// $[USART0]
// [USART0]$

// $[UART1]
// [UART1]$

// $[ULP_UART]
// [ULP_UART]$

// $[I2C0]
// [I2C0]$

// $[I2C1]
// [I2C1]$

// $[ULP_I2C]
// [ULP_I2C]$

// $[SSI_MASTER]
// SSI_MASTER MOSI_DATA0 on GPIO_26
#ifndef SSI_MASTER_MOSI_DATA0_PORT              
#define SSI_MASTER_MOSI_DATA0_PORT               HP
#endif
#ifndef SSI_MASTER_MOSI_DATA0_PIN               
#define SSI_MASTER_MOSI_DATA0_PIN                26
#endif
#ifndef SSI_MASTER_DATA0_LOC                    
#define SSI_MASTER_DATA0_LOC                     1
#endif

// SSI_MASTER MISO_DATA1 on GPIO_27
#ifndef SSI_MASTER_MISO_DATA1_PORT              
#define SSI_MASTER_MISO_DATA1_PORT               HP
#endif
#ifndef SSI_MASTER_MISO_DATA1_PIN               
#define SSI_MASTER_MISO_DATA1_PIN                27
#endif
#ifndef SSI_MASTER_DATA1_LOC                    
#define SSI_MASTER_DATA1_LOC                     4
#endif

// SSI_MASTER SCK_ on GPIO_25
#ifndef SSI_MASTER_SCK__PORT                    
#define SSI_MASTER_SCK__PORT                     HP
#endif
#ifndef SSI_MASTER_SCK__PIN                     
#define SSI_MASTER_SCK__PIN                      25
#endif
#ifndef SSI_MASTER_SCK_LOC                      
#define SSI_MASTER_SCK_LOC                       7
#endif

// SSI_MASTER CS0_ on GPIO_28
#ifndef SSI_MASTER_CS0__PORT                    
#define SSI_MASTER_CS0__PORT                     HP
#endif
#ifndef SSI_MASTER_CS0__PIN                     
#define SSI_MASTER_CS0__PIN                      28
#endif
#ifndef SSI_MASTER_CS0_LOC                      
#define SSI_MASTER_CS0_LOC                       10
#endif

// [SSI_MASTER]$

// $[SSI_SLAVE]
// [SSI_SLAVE]$

// $[ULP_SSI]
// [ULP_SSI]$

// $[GSPI_MASTER]
// GSPI_MASTER SCK_ on GPIO_25
#ifndef GSPI_MASTER_SCK__PORT                   
#define GSPI_MASTER_SCK__PORT                    HP
#endif
#ifndef GSPI_MASTER_SCK__PIN                    
#define GSPI_MASTER_SCK__PIN                     25
#endif
#ifndef GSPI_MASTER_SCK_LOC                     
#define GSPI_MASTER_SCK_LOC                      1
#endif

// GSPI_MASTER CS0_ on GPIO_28
#ifndef GSPI_MASTER_CS0__PORT                   
#define GSPI_MASTER_CS0__PORT                    HP
#endif
#ifndef GSPI_MASTER_CS0__PIN                    
#define GSPI_MASTER_CS0__PIN                     28
#endif
#ifndef GSPI_MASTER_CS0_LOC                     
#define GSPI_MASTER_CS0_LOC                      5
#endif

// GSPI_MASTER MOSI_ on GPIO_27
#ifndef GSPI_MASTER_MOSI__PORT                  
#define GSPI_MASTER_MOSI__PORT                   HP
#endif
#ifndef GSPI_MASTER_MOSI__PIN                   
#define GSPI_MASTER_MOSI__PIN                    27
#endif
#ifndef GSPI_MASTER_MOSI_LOC                    
#define GSPI_MASTER_MOSI_LOC                     17
#endif

// GSPI_MASTER MISO_ on GPIO_26
#ifndef GSPI_MASTER_MISO__PORT                  
#define GSPI_MASTER_MISO__PORT                   HP
#endif
#ifndef GSPI_MASTER_MISO__PIN                   
#define GSPI_MASTER_MISO__PIN                    26
#endif
#ifndef GSPI_MASTER_MISO_LOC                    
#define GSPI_MASTER_MISO_LOC                     22
#endif

// [GSPI_MASTER]$

// $[I2S0]
// [I2S0]$

// $[ULP_I2S]
// [ULP_I2S]$

// $[SCT]
// [SCT]$

// $[SIO]
// [SIO]$

// $[PWM]
// [PWM]$

// $[PWM_CH0]
// [PWM_CH0]$

// $[PWM_CH1]
// [PWM_CH1]$

// $[PWM_CH2]
// [PWM_CH2]$

// $[PWM_CH3]
// [PWM_CH3]$

// $[ADC_CH1]
// [ADC_CH1]$

// $[ADC_CH2]
// [ADC_CH2]$

// $[ADC_CH3]
// [ADC_CH3]$

// $[ADC_CH4]
// [ADC_CH4]$

// $[ADC_CH5]
// [ADC_CH5]$

// $[ADC_CH6]
// [ADC_CH6]$

// $[ADC_CH7]
// [ADC_CH7]$

// $[ADC_CH8]
// [ADC_CH8]$

// $[ADC_CH9]
// [ADC_CH9]$

// $[ADC_CH10]
// [ADC_CH10]$

// $[ADC_CH11]
// [ADC_CH11]$

// $[ADC_CH12]
// [ADC_CH12]$

// $[ADC_CH13]
// [ADC_CH13]$

// $[ADC_CH14]
// [ADC_CH14]$

// $[ADC_CH15]
// [ADC_CH15]$

// $[ADC_CH16]
// [ADC_CH16]$

// $[ADC_CH17]
// [ADC_CH17]$

// $[ADC_CH18]
// [ADC_CH18]$

// $[ADC_CH19]
// [ADC_CH19]$

// $[COMP1]
// [COMP1]$

// $[COMP2]
// [COMP2]$

// $[DAC0]
// [DAC0]$

// $[DAC1]
// [DAC1]$

// $[SYSRTC]
// [SYSRTC]$

// $[UULP_VBAT_GPIO]
// [UULP_VBAT_GPIO]$

// $[GPIO]
// [GPIO]$

// $[QEI]
// [QEI]$

// $[HSPI_SECONDARY]
// [HSPI_SECONDARY]$

// $[OPAMP1]
// [OPAMP1]$

// $[OPAMP2]
// [OPAMP2]$

// $[OPAMP3]
// [OPAMP3]$

// $[SDC_CH1]
// [SDC_CH1]$

// $[SDC_CH2]
// [SDC_CH2]$

// $[SDC_CH3]
// [SDC_CH3]$

// $[SDC_CH4]
// [SDC_CH4]$

// $[CUSTOM_PIN_NAME]
#ifndef _PORT                                   
#define _PORT                                    HP
#endif
#ifndef _PIN                                    
#define _PIN                                     6
#endif














































// [CUSTOM_PIN_NAME]$

#endif // PIN_CONFIG_H