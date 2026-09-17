/**
 * @file config.h
 *
 * @brief Configuration header file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Lisa Maria Odermatt, ETH Zurich
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
 * @name Board configurations
 * @{
 */
//!< Board type for WiUS firmware. Can be one of 0: "DK2605A", 1: "EK2708A", 2: "PK6031A", 3: "WIUS1".
#define WIUS_BOARD 3
/** @}
 */

/**
 * @name Logging configurations
 * @{
 */
//!< Maximum number of log callbacks that can be registered
#define LOG_MAX_CALLBACKS 1
//!< Size of the log buffer in bytes
#define LOG_BUFFER_SIZE 128
//!< Remove lifetime of log library (no deinitialization, no callback unregistration)
#define LOG_ONCE
#define LOG_NO_COLOR
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
#define WIUS_SPI_FREQ 5000000
//! Delay before deasserting software SPI CS after transfer completion in ns
#define WIUS_SPI_CS_DEASSERT_DELAY_NS 200
//! Delay after asserting software SPI CS before starting transfer in ns
#define WIUS_SPI_CS_ASSERT_DELAY_NS 200
//! Maximum transfer size that waits by polling an interrupt-updated flag
#define WIUS_SPI_SHORT_XFER_MAX 16
//! CS pin number for instance 0 (set to 0 if unused)
#define WIUS_SPI_EXT_CS0 53
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
#define TP_UDP_PACKET_AMT 1
//! Port on which UDP transfers happen
#define TP_UDP_PORT 50007
//! Port on which TCP transfers happen
#define TP_TCP_PORT 50008
//! FPGA Interrupt UULP gpio number
#define TP_GPIO_INT 2
//! FPGA Reset ULP gpio number
#define TP_GPIO_RESET 10
//! Stack size for main thread
#define TP_THREAD_STACK_MAIN 4500
//! Stack size for WiFi thread
#define TP_THREAD_STACK_WIFI 1500
/** @}
 */

/** @name TinyProbe AFE control configurations
 * @{
 */
//! Delay after SPI transfers in ns
#define TP_AFE_SPI_DELAY_NS 0
/** @}
 */

/** @name TinyProbe buffering configurations
 * @{
 */
//! Number of buffers available for data acquisition
#define TP_BUFFER_NUM 10
//! FIFO read size in bytes
#define TP_FIFO_READ_SIZE (TP_UDP_PACKET_SIZE * TP_UDP_PACKET_AMT)
//! Size of one buffer in bytes (FIFO read size + 2 bytes for packet index)
#define TP_BUFFER_SIZE (TP_FIFO_READ_SIZE + 2)
/** @}
 */

/** @name TinyProbe methods configurations
 * @{
 */
//! Response buffer size for JSON-RPC methods in bytes
#define TP_RESPONSE_BUFFER_SIZE 1024
//! Enable per-method DWT timing logs
#define TP_METHOD_TIMING 0
/** @}
 */

/** @name TinyProbe FPGA control configurations
 * @{
 */
//! Settling delay between an FPGA register write and its 0x4C verification read in ns
#define TP_FPGA_READBACK_TURNAROUND_DELAY_NS 200
//! SSI baud rate used by the FPGA dual-SPI register transport.
// Conservative bring-up rate for verified 0x32/0x4C FPGA register traffic.
// TX and AFE continue to use WIUS_SPI_FREQ independently.
#define TP_FPGA_DUAL_SPI_BAUDRATE 1000000UL
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
