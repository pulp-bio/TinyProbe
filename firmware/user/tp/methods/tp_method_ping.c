/**
 * @file tp_method_ping.c
 *
 * @brief TinyProbe ping method implementation file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 *
 * @ingroup tinyprobe_methods
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

#include "tp_method_ping.h"

#include "wius_tcp.h"

methods_status tp_method_ping(const methods_ping_args *args, void *userdata)
{
    UNUSED(userdata);

    sl_status_t status = SL_STATUS_OK;
    wius_tcp_server_message_t *msg = userdata;

    if (args->probe_id != TP_PROBE_ID)
    {
        log_warn("Invalid probe ID: %d", args->probe_id);
        return methods_status_INVALID_STATE;
    }

    char reply[32] = {0};
    snprintf(reply, sizeof(reply), "TinyProbe %lu", args->probe_id);

    status = wius_tcp_server_respond_udp(msg, TP_UDP_PORT, (uint8_t *)reply, strlen(reply));
    if (SL_STATUS_OK != status)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    return methods_status_OK;
}
