/**
 * @file config.h
 *
 * @brief Configuration header file
 *
 * @date 08.09.2025
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
 * @defgroup config_wius WiUS firmware configurations
 * This module documents the firmware configurations specific to WiUS.
 * @ingroup wius
 * @{
 */

/** @name WiUS SPI configurations
 * @{
 */
#define WIUS_SPI_FREQ 1000000   /**< SPI frequency in Hz (UNUSED, CHANGE IN sl_si91x_gspi_config.h) */
#define WIUS_SPI_RX_TIMEOUT 100 /**< Timeout for reception (ticks) */
#define WIUS_SPI_EXT_CS0 53     /**< Use seperate CS0 pin (set to 0 if unused) */
#define WIUS_SPI_EXT_CS1 0      /**< Use seperate CS1 pin (set to 0 if unused) */
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
#define WIUS_WIFI_DEVICE_NAME "WiUS" /**< WiFi device name */
/** @}
 */

/**
 * @name WiUS logging configurations
 * @{
 */
#define WIUS_LOG_LEVEL LOG_LEVEL_INFO /**< Log level for WiUS */
#define WIUS_LOG_GPIO_LED_RED 7       /**< Red LED gpio number */
#define WIUS_LOG_GPIO_LED_GREEN 6     /**< Green LED gpio number */
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
#define TP_TEST_MODE 0              /**< For testing acquisition code without confirmation from TinyProbe */
#define TP_PROBE_ID 1               /**< ID of the probe */
#define TP_WIFI_RX_BUFFER_SIZE 1472 /**< Size of the WiFi RX buffer */
#define TP_UDP_PACKET_SIZE 1000     /**< Size of one UDP packet (without header) */
#define TP_UDP_PACKET_AMT 4         /**< Number of packets to acquire per SPI before sending */
#define TP_UDP_PORT 50007           /**< Port on which UDP transfers happen */
#define TP_GPIO_INT 2               /**< FPGA Interrupt UULP gpio number */
#define TP_GPIO_RESET 10            /**< FPGA Reset ULP gpio number */
#define TP_THREAD_STACK_MAIN 16384  /**< Stack of main thread */
#define TP_THREAD_STACK_WIFI 1024   /**< Stack of WiFi thread */
/** @}
 */

/** @name TinyProbe AFE control configurations
 * @{
 */
#define TP_AFE_SPI_DELAY_NS 500000 /**< Delay after SPI transfers in ns */
/** @}
 */

/** @name TinyProbe buffering configurations
 * @{
 */
#define TP_BUFFER_NUM 2                                             /**< Number of buffers available */
#define TP_BUFFER_SIZE (TP_UDP_PACKET_SIZE * TP_UDP_PACKET_AMT + 2) /**< Size of one buffer in bytes */
/** @}
 */

/** @name TinyProbe commands configurations
 * @{
 */
#define TP_COMMAND_MAX 2048 /**< Maximum number of commands per WiFi package */
/** @}
 */

/** @name TinyProbe FPGA control configurations
 * @{
 */
#define TP_FPGA_SPI_DELAY_NS 50 /**< Delay after SPI transfers in ns */
/** @}
 */

/** @name TinyProbe MUX control configurations
 * @{
 */
#define TP_MUX_GPIO_EXTINT 3 /**< EXT INT MUX UULP gpio number */
#define TP_MUX_GPIO_AFETX 1  /**< AFE TX MUX ULP gpio number */
/** @}
 */

/** @name TinyProbe power control configurations
 * @{
 */
#define TP_POWER_GPIO_NEG_5V 2      /**< -5V ULP gpio number */
#define TP_POWER_GPIO_NEG_HV 52     /**< -HV gpio number */
#define TP_POWER_GPIO_POS_HV 56     /**< +HV gpio number */
#define TP_POWER_GPIO_LVDS_PWR_SW 8 /**< LVDS power switch ULP gpio number */
/** @}
 */

/** @name TinyProbe event flags
 * @{
 */
#define FLAG_CMD_RECEIVED (1 << 0)    /**< Command received flag */
#define FLAG_CMD_EXECUTED (1 << 1)    /**< Command done executing flag */
#define FLAG_SPI_TF0_DONE (1 << 2)    /**< SPI instance 0 transfer done flag */
#define FLAG_SPI_TF1_DONE (1 << 3)    /**< SPI instance 1 transfer done flag */
#define FLAG_FIFO_DATA_READY (1 << 4) /**< FIFO data ready flag */
                                      /** @}
                                       */

/** @} End of config_tinyprobe group */

// Don't touch this, here we transfer some configurations to all the drivers
#define RSI_DHCP_HOST_NAME WIUS_WIFI_DEVICE_NAME /**< Host name for DHCP */