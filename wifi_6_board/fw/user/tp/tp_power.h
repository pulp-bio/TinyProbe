/**
 * @file tp_power.h
 *
 * @brief Power Management driver for TinyProbe
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

/**
 * @brief Power domain enumeration
 *
 */
typedef enum tp_power_domain
{
    TP_POWER_DOMAIN_LVDS_2_5V = 0, /**< LVDS 2.5V */
    TP_POWER_DOMAIN_POS_HV,        /**< Positive high voltage */
    TP_POWER_DOMAIN_NEG_HV,        /**< Negative high voltage */
    TP_POWER_DOMAIN_NEG_5V,        /**< Negative 5V */
    TP_POWER_DOMAIN_PLL_PWD        /**< PLL power down */
} tp_power_domain_t;

/**
 * @brief Initialize the power control module
 *
 */
void tp_power_init(void);

/**
 * @brief Initialize the power domain of the TinyProbe
 *
 */
void tp_power_on(void);

/**
 * @brief Enable or disable a power domain
 *
 * @param domain: Power domain to enable or disable
 * @param enabled: True to enable, false to disable
 *
 */
void tp_power_set(tp_power_domain_t domain, bool enabled);