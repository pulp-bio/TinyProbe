/**
 * @file tp_command_ping.c
 *
 * @brief TinyProbe ping command implementation file
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

#include "tp_command_ping.h"

#include "tp.h"

sl_status_t tp_ping(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    (void)args;
    (void)args_length;

    sl_status_t status = SL_STATUS_OK;

    char reply[32] = {0};
    snprintf(reply, sizeof(reply), "TinyProbe %d", TP_PROBE_ID);
    CHECK_STATUS(wius_udp_sendto(&tp_socket, (const uint8_t *)reply, strlen(reply), client_ip, client_port));

    LOG_D("Done");

    return SL_STATUS_OK;
}