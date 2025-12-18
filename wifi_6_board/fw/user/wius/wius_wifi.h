/**
 * @file wius_wifi.h
 *
 * @brief WiUS WiFi implementation header file
 *
 * @date 17.12.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup wius
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

#include "common.h"

#include "sl_mdns.h"

/**
 * @brief WiFi performance profile enumeration
 *
 */
typedef enum wius_wifi_performance_profile
{
    WIUS_PERF_PROFILE_HIGHSPEED, /**< High speed */
    WIUS_PERF_PROFILE_LOWPOWER   /**< Low power */
} wius_wifi_performance_profile_t;

/**
 * @brief WiFi mDNS service structure
 *
 */
typedef struct wius_wifi_mdns
{
    sl_mdns_t handle;      /**< mDNS handle */
    char *protocol;        /**< Protocol string ("udp" or "tcp") */
    char *host_name;       /**< Host name string (without .local) */
    char *service_name;    /**< Service name string */
    char *service_message; /**< Service message string */
    uint16_t port;         /**< Service port number */
} wius_wifi_mdns_t;

/**
 * @brief Initialize the WiFi client interface
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: net initialization or bring up failed
 *
 */
sl_status_t wius_wifi_init(void);

/**
 * @brief Deinitialize the WiFi client interface
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: net deinitialization failed
 *
 */
sl_status_t wius_wifi_deinit(void);

/**
 * @brief Initialize an mDNS service structure
 *
 * @param mdns: Pointer to the mDNS service structure
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_INVALID_PARAMETER: Invalid parameter (null pointer or invalid host name)
 * @retval other: mDNS or interface initialization failed
 *
 */
sl_status_t wius_wifi_mdns_init(wius_wifi_mdns_t *mdns);

/**
 * @brief Add an mDNS service
 *
 * @param mdns: Pointer to the mDNS service structure
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: mDNS service addition failed
 *
 */
sl_status_t wius_wifi_mdns_add(wius_wifi_mdns_t *mdns);

/**
 * @brief Set the WiFi performance profile
 *
 * @param profile: Pointer to the performance profile enumeration (@ref wius_wifi_performance_profile_t)
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_INVALID_PARAMETER: Invalid performance profile
 * @retval SL_STATUS_SI91X_POWER_SAVE_NOT_SUPPORTED: Profile not applied
 * @retval other: Performance profile setting failed
 *
 */
sl_status_t wius_wifi_set_performance_profile(wius_wifi_performance_profile_t profile);