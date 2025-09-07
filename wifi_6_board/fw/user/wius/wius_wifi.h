/**
 * @file wius_wifi.h
 *
 * @brief WiFi implementation for WiUS
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup wius
 *
 */

#pragma once

#include "common.h"

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