/**
 * @file config.h
 *
 * @brief Configuration header file
 *
 * @date 17.12.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup common
 *
 * @parblock
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * @endparblock
 *
 */

#pragma once

#include "env.h"

/**
 * @defgroup config_common Common firmware configurations
 * This module documents the common firmware configurations.
 * @ingroup common
 * @{
 */

/**
 * @name Logging configurations
 * @{
 */
//! Log level to use
#define LOG_LEVEL LOG_LEVEL_INFO
//! Buffer size to use per log line
#define LOG_BUFFER_SIZE 256
/** @}
 */

/** @} End of config_common group */

/**
 * @defgroup config_wius WiUS firmware configurations
 * This module documents the firmware configurations specific to WiUS.
 * @ingroup wius
 * @{
 */

/** @name WiUS SPI configurations
 * @{
 */
//! SPI clock frequency in Hz
#define WIUS_SPI_FREQ 40000000
//! SPI timeout for transmission in ticks
#define WIUS_SPI_RX_TIMEOUT 100
//! CS pin number for instance 0 (set to 0 if unused)
#define WIUS_SPI_EXT_CS0 53
//! CS pin number for instance 1 (set to 0 if unused)
#define WIUS_SPI_EXT_CS1 0
/** @}
 */

/** @name WiUS WiFi configurations
 * @{
 */
#ifndef WIUS_WIFI_SSID
#error "Please define WIUS_WIFI_SSID in env.h"
#endif
#ifndef WIUS_WIFI_PASS
#error "Please define WIUS_WIFI_PASS in env.h"
#endif
//! Device name for WiFi
#define WIUS_WIFI_DEVICE_NAME "WiUS"
/** @}
 */

/** @} End of config_wius group */

/** @defgroup config_tinyprobe TinyProbe firmware configurations
 *  This module documents the firmware configurations specific to TinyProbe.
 *  @ingroup tinyprobe
 *  @{
 */

/** @name TinyProbe general configurations
 * @{
 */
//! Enable test mode (1=enabled, 0=disabled). Used for testing acquisition code without actual TinyProbe hardware.
#define TP_TEST_MODE 0
//! ID of the probe (used for Ping responses)
#define TP_PROBE_ID 1
//! Size of the WiFi RX buffer
#define TP_WIFI_RX_BUFFER_SIZE 1472
//! Size of one UDP packet (no header)
#define TP_UDP_PACKET_SIZE 1000
//! Number of packets to acquire per SPI before sending
#define TP_UDP_PACKET_AMT 4
//! Port on which UDP transfers happen
#define TP_UDP_PORT 50007
//! Port on which TCP transfers happen
#define TP_TCP_PORT 50008
//! FPGA Interrupt UULP gpio number
#define TP_GPIO_INT 2
//! FPGA Reset ULP gpio number
#define TP_GPIO_RESET 10
//! Stack size for main thread
#define TP_THREAD_STACK_MAIN 6000
//! Stack size for WiFi thread
#define TP_THREAD_STACK_WIFI 2000
/** @}
 */

/** @name TinyProbe AFE control configurations
 * @{
 */
//! Delay after SPI transfers in ns
#define TP_AFE_SPI_DELAY_NS 500000
/** @}
 */

/** @name TinyProbe buffering configurations
 * @{
 */
//! Number of buffers available for data acquisition
#define TP_BUFFER_NUM 5
//! Size of one buffer in bytes
#define TP_BUFFER_SIZE (TP_UDP_PACKET_SIZE * TP_UDP_PACKET_AMT + 2)
/** @}
 */

/** @name TinyProbe commands configurations
 * @{
 */
//! Maximum number of commands per WiFi package
#define TP_COMMAND_MAX 128
/** @}
 */

/** @name TinyProbe FPGA control configurations
 * @{
 */
//! Delay after SPI transfers in ns
#define TP_FPGA_SPI_DELAY_NS 50
/** @}
 */

/** @name TinyProbe MUX control configurations
 * @{
 */
//! EXT INT MUX UULP gpio number
#define TP_MUX_GPIO_EXTINT 3
//! AFE TX MUX ULP gpio number
#define TP_MUX_GPIO_AFETX 1
/** @}
 */

/** @name TinyProbe power control configurations
 * @{
 */
//! -5V ULP gpio number
#define TP_POWER_GPIO_NEG_5V 2
//! -HV gpio number
#define TP_POWER_GPIO_NEG_HV 52
//! +HV gpio number
#define TP_POWER_GPIO_POS_HV 56
//! LVDS power switch ULP gpio number
#define TP_POWER_GPIO_LVDS_PWR_SW 8
/** @}
 */

/** @} End of config_tinyprobe group */

// Don't touch this, here we transfer some configurations to all the drivers
#define RSI_DHCP_HOST_NAME WIUS_WIFI_DEVICE_NAME /**< Host name for DHCP */
