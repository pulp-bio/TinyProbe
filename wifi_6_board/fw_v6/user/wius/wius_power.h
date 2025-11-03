/**
 * @file wius_power.h
 *
 * @brief Power management for WiUS
 *
 * @date 08.09.2025
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