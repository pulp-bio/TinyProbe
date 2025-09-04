/**
 * @file tp_power.h
 *
 * @brief Power Management driver for TinyProbe
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
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