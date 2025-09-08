/**
 * @file tp_mux.h
 *
 * @brief SPI MUX driver for TinyProbe
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