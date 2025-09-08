/**
 * @file tp_mux.h
 *
 * @brief SPI MUX driver for TinyProbe
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
 * @brief Mux selection enumeration
 *
 */
typedef enum tp_mux
{
    TP_MUX_PLL = 0b00,  /**< PLL Mux */
    TP_MUX_FPGA = 0b01, /**< FPGA Mux */
    TP_MUX_AFE = 0b10,  /**< AFE Mux */
    TP_MUX_TX = 0b11    /**< TX Mux */
} tp_mux_t;

/**
 * @brief MUX initialization
 *
 */
void tp_mux_init(void);

/**
 * @brief MUX select
 *
 * @param[in] mux Mux to select
 */
void tp_mux_select(tp_mux_t mux);