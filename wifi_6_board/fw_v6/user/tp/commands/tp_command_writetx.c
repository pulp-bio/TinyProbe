/**
 * @file tp_command_writetx.c
 *
 * @brief TinyProbe TX write command implementation file
 *
 * @date 26.11.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
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

#include "tp_command_writetx.h"

#include "tp_tx.h"

sl_status_t tp_write_tx(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;
    sl_status_t status = SL_STATUS_OK;

    uint16_t tx_reg_addr = GET(args, uint16_t, 0);
    uint32_t tx_reg_value = GET(args, uint32_t, 2);

    CHECK_STATUS(tp_tx_write_reg(tx_reg_addr, tx_reg_value));

    LOG_D("Done");

    return SL_STATUS_OK;
}