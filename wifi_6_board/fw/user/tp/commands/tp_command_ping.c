/**
 * @file tp_command_ping.c
 *
 * @brief TinyProbe ping command implementation file
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

#include "tp_command_ping.h"

#include "tp.h"

sl_status_t tp_ping(uint8_t *args, uint16_t args_length, wius_tcp_server_message_t *msg)
{
    LOG_D("Executing");

    (void)args_length;

    sl_status_t status = SL_STATUS_OK;

    if (args[0] != TP_PROBE_ID)
    {
        LOG_W("Ping probe ID %d does not match expected %d", args[0], TP_PROBE_ID);
        return SL_STATUS_INVALID_PARAMETER;
    }

    char reply[32] = {0};
    snprintf(reply, sizeof(reply), "TinyProbe %d", TP_PROBE_ID);
    CHECK_STATUS(wius_tcp_server_respond_udp(msg, TP_UDP_PORT, (uint8_t *)reply, strlen(reply)));

    LOG_D("Done");

    return SL_STATUS_OK;
}