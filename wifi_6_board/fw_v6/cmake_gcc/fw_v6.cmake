####################################################################
# Automatically-generated file. Do not edit!                       #
####################################################################

set(SDK_PATH "C:/Users/cedr0/.silabs/slt/installs/conan/p/simpleb526998f4a4d/p")
set(COPIED_SDK_PATH "simplicity_sdk_2025.6.2")
set(PKG_PATH "C:/Users/cedr0/.silabs/slt/installs")

add_library(slc OBJECT
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/board/silabs/src/rsi_board.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/common/src/sl_utility.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/common/src/malloc_thread_safety.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/common/src/syscalls.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/cmsis_driver/GSPI.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/cmsis_driver/SPI.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/aux_reference_volt_config.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_adc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_dac.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_gspi.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_opamp.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_spi.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/sl_si91x_m4_ps.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/clock_manager/src/sl_si91x_clock_manager.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/clock_manager/src/sli_si91x_clock_manager.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/power_manager/src/sl_si91x_power_manager.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/power_manager/src/sli_si91x_power_manager.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/power_manager/src/sli_si91x_power_manager_wakeup_init.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_bod.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_adc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_bjt_temperature_sensor.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_dma.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_gspi.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_ssi.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/asynchronous_socket/src/sl_si91x_socket.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/icmp/sl_net_ping.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/memory/malloc_buffers.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_callback_framework.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/src/sli_net_si91x_utility.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/socket/src/sl_si91x_socket_utility.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/src/sl_rsi_utility.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/src/sl_si91x_driver.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/protocol/wifi/si91x/sl_wifi.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/protocol/wifi/src/sl_wifi_basic_credentials.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/protocol/wifi/src/sl_wifi_callback_framework.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/bsd_socket/si91x_socket/sl_si91x_bsd_socket.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/mdns/si91x/sl_mdns.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/network_manager/src/sl_net.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/network_manager/src/sl_net_basic_certificate_store.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/network_manager/src/sl_net_basic_profiles.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/network_manager/src/sl_net_credentials.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/network_manager/src/sli_net_common_utility.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/sli_si91x_wifi_event_handler/src/sli_si91x_wifi_event_handler.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/sli_wifi_command_engine/src/sli_wifi_command_engine.c"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/third_party/silicon_labs/freertos/src/sl_si91x_low_power_tickless_mode.c"
    "${SDK_PATH}/platform/CMSIS/RTOS2/Source/os_systick.c"
    "${SDK_PATH}/platform/common/src/sl_assert.c"
    "${SDK_PATH}/platform/common/src/sl_cmsis_os2_common.c"
    "${SDK_PATH}/platform/common/src/sl_core_cortexm.c"
    "${SDK_PATH}/platform/common/src/sl_slist.c"
    "${SDK_PATH}/platform/common/src/sl_string.c"
    "${SDK_PATH}/platform/common/src/sl_syscalls.c"
    "${SDK_PATH}/platform/common/src/sli_cmsis_os2_ext_task_register.c"
    "${SDK_PATH}/platform/service/memory_manager/src/sl_memory_manager_cpp.cpp"
    "${SDK_PATH}/platform/service/memory_manager/src/sl_memory_manager_pool.c"
    "${SDK_PATH}/platform/service/memory_manager/src/sl_memory_manager_redirect.c"
    "${SDK_PATH}/platform/service/sl_main/src/rtos/main_retarget.c"
    "${SDK_PATH}/platform/service/sl_main/src/sl_main_init.c"
    "${SDK_PATH}/platform/service/sl_main/src/sl_main_init_memory.c"
    "${SDK_PATH}/platform/service/sl_main/src/sl_main_kernel.c"
    "${SDK_PATH}/platform/service/sleeptimer/src/sl_sleeptimer.c"
    "${SDK_PATH}/util/third_party/freertos/cmsis/Source/cmsis_os2.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/croutine.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/event_groups.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/list.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/portable/MemMang/heap_3.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/queue.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/stream_buffer.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/tasks.c"
    "${SDK_PATH}/util/third_party/freertos/kernel/timers.c"
    "../autogen/sl_event_handler.c"
    "../autogen/sl_si91x_power_manager_handler.c"
    "../autogen/sl_si91x_power_manager_wakeup_handler.c"
    "../main.c"
)

target_include_directories(slc PUBLIC
   "../config"
   "../autogen"
   "../."
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/protocol/wifi/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/bsd_socket/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/bsd_socket/si91x_socket"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/cmsis_driver/CMSIS/Driver/Include"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/cmsis_driver"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/common/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/mdns/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/service/network_manager/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/rom_driver/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/chip/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/board/silabs/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/core/config"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_api/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/clock_manager/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/power_manager/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/asynchronous_socket/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/errno/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/firmware_upgrade"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/sl_net/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/icmp"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/socket/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/inc/mqtt/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/wireless/ahb_interface/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/sli_wifi_command_engine/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/device/silabs/si91x/mcu/drivers/systemlevel/inc"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/resources/defaults"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/resources/certificates"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/resources/html"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/resources/other"
    "${SDK_PATH}/../../wisece6a05cd369ee2/p/components/common/inc"
    "${SDK_PATH}/platform/common/inc"
    "${SDK_PATH}/platform/CMSIS/Core/Include"
    "${SDK_PATH}/platform/CMSIS/RTOS2/Include"
    "${SDK_PATH}/platform/emlib/inc"
    "${SDK_PATH}/util/third_party/freertos/kernel/include"
    "${SDK_PATH}/util/third_party/freertos/cmsis/Include"
    "${SDK_PATH}/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F"
    "${SDK_PATH}/platform/service/memory_manager/inc"
    "${SDK_PATH}/platform/service/memory_manager/src"
    "${SDK_PATH}/platform/service/sl_main/inc"
    "${SDK_PATH}/platform/service/sl_main/src"
    "${SDK_PATH}/platform/service/sleeptimer/inc"
)

target_compile_definitions(slc PUBLIC
    "SLI_SI91X_EMPTY_PROJECT=1"
    "SIWG917M111MGTBA=1"
    "SLI_SI917=1"
    "SLI_SI917B0=1"
    "SLI_SI91X_MCU_ENABLE_FLASH_BASED_EXECUTION=1"
    "SLI_SI91X_MCU_EXTERNAL_LDO_FOR_PSRAM=1"
    "SLI_SI91X_MCU_COMMON_FLASH_MODE=1"
    "SLI_SI91X_MCU_CONFIG_RADIO_BOARD_BASE_VER=1"
    "SLI_SI91X_MCU_CONFIG_RADIO_BOARD_VER2=1"
    "SL_BOARD_NAME=\"BRD4002A\""
    "SL_BOARD_REV=\"A07\""
    "SLI_SI91X_MCU_ENABLE_RAM_BASED_EXECUTION=1"
    "__FREERTOS_OS_WISECONNECT=1"
    "SLI_SI91X_INTERNAL_MDNS=1"
    "SL_NET_COMPONENT_INCLUDED=1"
    "__STATIC_INLINE=static inline"
    "CLOCK_ROMDRIVER_PRESENT=1"
    "ULPSS_CLOCK_ROMDRIVER_PRESENT=1"
    "SL_SI91X_BOARD_INIT=1"
    "SRAM_BASE=0x0cUL"
    "SRAM_SIZE=0x2fc00UL"
    "SLI_CODE_CLASSIFICATION_DISABLE=1"
    "SLI_SI91X_MCU_ENABLE_IPMU_APIS=1"
    "SL_SI91X_SOC_MODE=1"
    "CRC_ROMDRIVER_PRESENT=1"
    "SPI_MULTI_SLAVE=1"
    "DEBUG_ENABLE=1"
    "DEBUG_UART=1"
    "ENABLE_DEBUG_MODULE=1"
    "SL_SI91X_SI917_RAM_MEM_CONFIG=1"
    "SL_SI91X_TICKLESS_MODE=1"
    "UDMA_ROMDRIVER_PRESENT=1"
    "GSPI_CONFIG=1"
    "GSPI_MULTI_SLAVE=1"
    "SL_SI91X_GSPI_DMA=1"
    "SL_SI91X_REQUIRES_INTF_PLL=1"
    "SLI_WIRELESS_COMPONENT_PRESENT=1"
    "SLI_SI91X_OFFLOAD_NETWORK_STACK=1"
    "SI917=1"
    "SLI_SI91X_ENABLE_OS=1"
    "SLI_SI91X_MCU_INTERFACE=1"
    "TA_DEEP_SLEEP_COMMON_FLASH=1"
    "SLI_SI91X_SOCKETS=1"
    "SL_SI91X_SSI_DMA=1"
    "SSI_CONFIG=1"
    "SSI_DUAL_QUAD_COMPONENT=1"
    "SSI_INSTANCE_CONFIG=1"
    "SI91X_PLATFORM=1"
    "SI91X_SYSRTC_PRESENT=1"
    "SL_SLEEP_TIMER=1"
    "__WEAK=__attribute__((weak))"
    "PLL_ROMDRIVER_PRESENT=1"
    "SL_SI91X_POWER_MANAGER_UC_AVAILABLE=1"
    "SL_WIFI_COMPONENT_INCLUDED=1"
    "configNUM_SDK_THREAD_LOCAL_STORAGE_POINTERS=2"
    "SL_COMPONENT_CATALOG_PRESENT=1"
    "SL_CODE_COMPONENT_FREERTOS_KERNEL=freertos_kernel"
    "SL_CODE_COMPONENT_CORE=core"
    "SL_CODE_COMPONENT_SLEEPTIMER=sleeptimer"
)

target_link_libraries(slc PUBLIC
    "-Wl,--start-group"
    "gcc"
    "nosys"
    "c"
    "m"
    "-Wl,--end-group"
)
target_compile_options(slc PUBLIC
    $<$<COMPILE_LANGUAGE:C>:-mcpu=cortex-m4>
    $<$<COMPILE_LANGUAGE:C>:-mthumb>
    $<$<COMPILE_LANGUAGE:C>:-mfpu=fpv4-sp-d16>
    $<$<COMPILE_LANGUAGE:C>:-mfloat-abi=softfp>
    $<$<COMPILE_LANGUAGE:C>:-Wall>
    $<$<COMPILE_LANGUAGE:C>:-Wextra>
    $<$<COMPILE_LANGUAGE:C>:-Os>
    $<$<COMPILE_LANGUAGE:C>:-fdata-sections>
    $<$<COMPILE_LANGUAGE:C>:-ffunction-sections>
    $<$<COMPILE_LANGUAGE:C>:-fomit-frame-pointer>
    $<$<COMPILE_LANGUAGE:C>:-g>
    "$<$<COMPILE_LANGUAGE:C>:SHELL:-Wall -Werror>"
    $<$<COMPILE_LANGUAGE:C>:-Wno-error=deprecated-declarations>
    "$<$<COMPILE_LANGUAGE:C>:SHELL:-Wall -Werror -Wno-error=deprecated-declarations>"
    $<$<COMPILE_LANGUAGE:C>:-mcpu=cortex-m4>
    $<$<COMPILE_LANGUAGE:C>:-fno-lto>
    $<$<COMPILE_LANGUAGE:C>:--specs=nano.specs>
    $<$<COMPILE_LANGUAGE:CXX>:-mcpu=cortex-m4>
    $<$<COMPILE_LANGUAGE:CXX>:-mthumb>
    $<$<COMPILE_LANGUAGE:CXX>:-mfpu=fpv4-sp-d16>
    $<$<COMPILE_LANGUAGE:CXX>:-mfloat-abi=softfp>
    $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
    $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
    $<$<COMPILE_LANGUAGE:CXX>:-Wall>
    $<$<COMPILE_LANGUAGE:CXX>:-Wextra>
    $<$<COMPILE_LANGUAGE:CXX>:-Os>
    $<$<COMPILE_LANGUAGE:CXX>:-fdata-sections>
    $<$<COMPILE_LANGUAGE:CXX>:-ffunction-sections>
    $<$<COMPILE_LANGUAGE:CXX>:-fomit-frame-pointer>
    $<$<COMPILE_LANGUAGE:CXX>:-g>
    "$<$<COMPILE_LANGUAGE:CXX>:SHELL:-Wall -Werror>"
    $<$<COMPILE_LANGUAGE:CXX>:-Wno-error=deprecated-declarations>
    "$<$<COMPILE_LANGUAGE:CXX>:SHELL:-Wall -Werror -Wno-error=deprecated-declarations>"
    $<$<COMPILE_LANGUAGE:CXX>:-mcpu=cortex-m4>
    $<$<COMPILE_LANGUAGE:CXX>:-fno-lto>
    $<$<COMPILE_LANGUAGE:CXX>:--specs=nano.specs>
    $<$<COMPILE_LANGUAGE:ASM>:-mcpu=cortex-m4>
    $<$<COMPILE_LANGUAGE:ASM>:-mthumb>
    $<$<COMPILE_LANGUAGE:ASM>:-mfpu=fpv4-sp-d16>
    $<$<COMPILE_LANGUAGE:ASM>:-mfloat-abi=softfp>
    "$<$<COMPILE_LANGUAGE:ASM>:SHELL:-x assembler-with-cpp>"
)

set(post_build_command ${POST_BUILD_EXE} postbuild "./fw_v6.slpb" --parameter build_dir:"$<TARGET_FILE_DIR:fw_v6>")
set_property(TARGET slc PROPERTY C_STANDARD 17)
set_property(TARGET slc PROPERTY CXX_STANDARD 17)
set_property(TARGET slc PROPERTY CXX_EXTENSIONS OFF)

target_link_options(slc INTERFACE
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=softfp
    -T${CMAKE_CURRENT_LIST_DIR}/../autogen/linkerfile_SoC.ld
    --specs=nano.specs
    "SHELL:-Xlinker -Map=$<TARGET_FILE_DIR:fw_v6>/fw_v6.map"
    "SHELL:-u _printf_float"
    -Wl,--wrap=main
    -fno-lto
    -Wl,--gc-sections
)

# BEGIN_SIMPLICITY_STUDIO_METADATA=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=END_SIMPLICITY_STUDIO_METADATA