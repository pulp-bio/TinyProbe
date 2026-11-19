/**
 * @file tp_spi.h
 *
 * @brief TinyProbe shared SPI bus API
 *
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 * @author Lisa Maria Odermatt, ETH Zurich
 *
 * @ingroup tinyprobe
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

#include "tp_mux.h"

/**
 * @brief Initialize primary SSI with the FPGA base clock mode and software chip select.
 *
 * @return SL_STATUS_OK on success or an SSI initialization error.
 */
sl_status_t tp_spi_init(void);

/**
 * @brief Route the shared SPI bus to the requested target and wait for the mux to settle.
 *
 * AFE and TX use Mode 0. The FPGA HAL restores Mode 1 and dual-data framing
 * when it starts a transfer. Selecting PLL routes chip select to the PLL.
 *
 * @param[in] target Destination on the TinyProbe SPI mux.
 * @retval SL_STATUS_OK The bus is routed and the mux settling delay has elapsed.
 * @retval SL_STATUS_INVALID_PARAMETER The target is invalid.
 * @return An SSI reconfiguration error if the external-device mode could not be set.
 */
sl_status_t tp_spi_select(tp_mux_t target);
