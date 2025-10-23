/**
 * @file tp_command_ctrlpwr.c
 *
 * @brief TinyProbe control power command implementation file
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

#include "tp_command_ctrlpwr.h"

#include "tp_power.h"

sl_status_t tp_ctrl_pwr(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args_length;

    tp_power_domain_t domain = GET(args, tp_power_domain_t, 0);
    uint8_t enabled = GET(args, uint8_t, 1);
    tp_power_set(domain, enabled ? true : false);

    LOG_D("Done");

    return SL_STATUS_OK;
}