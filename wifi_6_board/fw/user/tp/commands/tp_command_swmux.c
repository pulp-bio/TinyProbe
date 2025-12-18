/**
 * @file tp_command_swmux.c
 *
 * @brief TinyProbe SPI MUX command implementation file
 *
 * @date 17.12.2025
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

#include "tp_command_swmux.h"

#include "tp_mux.h"

sl_status_t tp_sw_mux(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    UNUSED(args_length);

    tp_mux_t mux = GET(args, tp_mux_t, 0);
    tp_mux_select(mux);

    LOG_D("Done");

    return SL_STATUS_OK;
}