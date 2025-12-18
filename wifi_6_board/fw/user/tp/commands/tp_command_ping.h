/**
 * @file tp_command_ping.h
 *
 * @brief TinyProbe ping command header file
 *
 * @date 17.12.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 *
 * @ingroup tinyprobe_commands
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

/**
 * @brief Ping command
 *
 * @param args: Command arguments
 * @param args_length: Length of command arguments
 * @param msg: Incoming TCP server message for UDP reply
 *
 * @return sl_status_t Status code of the operation
 *
 */
sl_status_t tp_ping(uint8_t *args, uint16_t args_length, wius_tcp_server_message_t *msg);