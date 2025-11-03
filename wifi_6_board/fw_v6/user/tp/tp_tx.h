/**
 * @file tp_tx.h
 *
 * @brief TX chip driver for TinyProbe
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
 * @brief TX initialization
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 * @note This function must be called before any other TX function
 *
 */
sl_status_t tp_tx_init(void);

/**
 * @brief Write to a register of the TX
 *
 * @param address: Address of the register to write to
 * @param value: Value to write to the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_tx_write_reg(uint16_t address, uint32_t value);

/**
 * @brief Write to a register of the TX and check if the write was successful
 *
 * @param address: Address of the register to write to
 * @param value: Value to write to the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Write was not successful
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_tx_write_reg_safe(uint16_t address, uint32_t value);

/**
 * @brief Read from a register of the TX
 *
 * @param address: Address of the register to read from
 * @param value: Pointer to the value read from the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during reading from registers
 *
 */
sl_status_t tp_tx_read_reg(uint16_t address, uint32_t *value);