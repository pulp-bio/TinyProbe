/**
 * @file tp_methods.h
 *
 * @brief TinyProbe methods header file
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

#pragma once

#include "common.h"
#include "wius_tcp.h"

#include "methods/tp_method_controlpower.h"
#include "methods/tp_method_controlspi.h"
#include "methods/tp_method_delayms.h"
#include "methods/tp_method_delayns.h"
#include "methods/tp_method_ping.h"
#include "methods/tp_method_setloglevel.h"
#include "methods/tp_method_triggershot.h"
#include "methods/tp_method_writeafe.h"
#include "methods/tp_method_writefpga.h"
#include "methods/tp_method_writetx.h"

//! All TinyProbe methods must be listed here
#define TP_METHODS \
    X(controlpower) \
    X(controlspi) \
    X(delayms) \
    X(delayns) \
    X(ping) \
    X(setloglevel) \
    X(triggershot) \
    X(writeafe) \
    X(writefpga) \
    X(writetx)

/**
 * @brief Export all TinyProbe methods
 *
 */
void tp_methods_handle(wius_tcp_server_message_t *request, void (*sender)(const char *response, size_t response_len));
