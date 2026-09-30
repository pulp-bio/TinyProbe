/**
 * @file tp_methods.c
 *
 * @brief TinyProbe methods implementation file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
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

#include "tp_methods.h"

#include "sl_si91x_clock_manager.h"

#include <pb_decode.h>
#include <pb_encode.h>

#include "methods.pb.h"

uint8_t response_data[methods_response_size];

methods_request req = methods_request_init_default;
methods_response rsp = methods_response_init_default;

void tp_methods_handle(wius_tcp_server_message_t *request, void (*sender)(const char *response, size_t response_len))
{
    // log_trace("Decoding request with %u bytes of data", (unsigned)request->length);
    pb_istream_t istream = pb_istream_from_buffer(request->data, request->length);
    // log_trace("Created istream for request data");
    if (!pb_decode(&istream, methods_request_fields, &req))
    {
        log_error("Failed to decode request: %s", istream.errmsg ? istream.errmsg : "unknown decode error");
        return;
    }
    // log_debug("Decoded request with %u commands", (unsigned)req.cmd_count);

    rsp.status_count = req.cmd_count;
    for (size_t i = 0; i < rsp.status_count; i++) {
        rsp.status[i] = methods_status_OK;
    }

    size_t triggered_shots = 0;

    int loop_iterations = -1;
    void *userdata = request;
    for (size_t i = 0; i < req.cmd_count; i++)
    {
        const methods_cmd *cmd = &req.cmd[i];
        methods_status status = methods_status_OK;

        if (cmd->which_args == methods_cmd_triggershot_tag) {
            log_debug("Shot at %u", time_ms());
        }

#if TP_METHOD_TIMING
        uint32_t time_start = DWT->CYCCNT;
#endif
        switch (cmd->which_args)
        {

#define X(name)                                               \
    case methods_cmd_##name##_tag:                            \
        status = tp_method_##name(&cmd->args.name, userdata); \
        break;
            TP_METHODS
#undef X
        case methods_cmd_loop_tag:
            // log_debug("Handling method %u: loop", i);
            if (loop_iterations < 0)
            {
                loop_iterations = cmd->args.loop.iterations;
            }
            if (loop_iterations > 0)
            {
                // log_debug("Looping back to command index: %d, remaining iterations: %d", cmd->args.loop.command_index, loop_iterations);
                i = cmd->args.loop.command_index - 1; // -1 because the for loop will increment i
                loop_iterations--;
            }
            else
            {
                // log_debug("No more iterations left for loop");
            }
            status = methods_status_OK;
            break;
        default:
            log_warn("Unknown method: %d", cmd->which_args);
            status = methods_status_INVALID_STATE;
            break;
        }
#if TP_METHOD_TIMING
        uint32_t time_end = DWT->CYCCNT;
        uint32_t time_elapsed = time_end - time_start;
        log_debug("%u %u %u", i, cmd->which_args, time_elapsed);
#endif

        if (cmd->which_args == methods_cmd_triggershot_tag && status == methods_status_OK) {
            triggered_shots++;
        }

        if (rsp.status[i] == methods_status_OK) {
            rsp.status[i] = status;

        }
        if (methods_status_OK != status) {
            log_error("Error handling method %d: %d", cmd->which_args, status);
        }
    }

#if TP_METHOD_TIMING
    log_info("Triggered total %u shots", triggered_shots);
#else
    UNUSED(triggered_shots);
#endif

    pb_ostream_t ostream = pb_ostream_from_buffer(response_data, sizeof(response_data));
    if (!pb_encode(&ostream, methods_response_fields, &rsp))
    {
        log_error("Failed to encode response: %s", ostream.errmsg ? ostream.errmsg : "unknown encode error");
        return;
    }

    sender((const char *)response_data, ostream.bytes_written);
}
