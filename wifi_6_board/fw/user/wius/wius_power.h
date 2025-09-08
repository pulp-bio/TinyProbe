/**
 * @file wius_power.h
 *
 * @brief Power management for WiUS
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup wius
 *
 */

#pragma once

#include "common.h"

typedef enum wius_power_mode
{
    WIUS_POWER_MODE_LOW = 0, /**< Low power */
    WIUS_POWER_MODE_HIGH     /**< High power */
} wius_power_mode_t;

/**
 * @brief Initialize the power management module
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Power management initialization failed
 *
 */
sl_status_t wius_power_init(void);

/**
 * @brief Set the power mode
 *
 * @param mode: Power mode to set (@ref wius_power_mode_t)
 *
 */
sl_status_t wius_power_set(wius_power_mode_t mode);