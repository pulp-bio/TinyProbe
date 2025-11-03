/**
 * @file tp_command.h
 *
 * @brief Command handler for TinyProbe
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

#include "wius_tcp.h"

/**
 * @brief Command IDs enumeration
 *
 */
typedef enum tp_cmd_id
{
    TP_CMD_PING = 0,
    TP_CMD_EN_REPLIES,
    TP_CMD_SW_MUX,
    TP_CMD_WRITE_SPI,
    TP_CMD_WRITE_FPGA,
    TP_CMD_WRITE_AFE,
    TP_CMD_WRITE_TX,
    TP_CMD_DELAY_NS,
    TP_CMD_SLEEP_MS,
    TP_CMD_CTRL_PWR,
    TP_CMD_TRIGGER_SHOT,
    TP_CMD_SET_POWERSAVE,
    TP_CMD_ID_MAX
} tp_command_id_t;

/**
 * @brief Command structure
 *
 * <table class="tg">
 * <tbody>
 *   <tr>
 *     <th class="tg-1wig">Byte</th>
 *     <th class="tg-0lax">0</th>
 *     <th class="tg-0lax">1</th>
 *     <th class="tg-0lax">2</th>
 *     <th class="tg-0lax">3</th>
 *     <th class="tg-0lax">4</th>
 *     <th class="tg-0lax">5 ... (4 + ARG_LEN_0)</th>
 *     <th class="tg-0lax">(5 + ARG_LEN_0)</th>
 *     <th class="tg-0lax">...</th>
 *   </tr>
 *   <tr>
 *     <td class="tg-1wig">Description</td>
 *     <td class="tg-0lax" colspan="2">number of commands<br><span style="font-style:italic">[uint16_t]</span></td>
 *     <td class="tg-0lax">Command 0 ID<br><span style="font-style:italic">[uint8_t]</span></td>
 *     <td class="tg-0lax" colspan="2">CMD arguments length<br><span style="font-style:italic">[uint16_t]</span></td>
 *     <td class="tg-0lax">Argument 0</td>
 *     <td class="tg-0lax">Argument 1</td>
 *     <td class="tg-0lax">...</td>
 *   </tr>
 * </tbody>
 * </table>
 *
 */
typedef struct tp_cmd
{
    tp_command_id_t id;
    uint8_t *args;
    size_t args_length;
} tp_command_t;

/**
 * @brief Parse a command from a buffer
 *
 * @param buffer The buffer containing the command
 * @param buffer_length The length of the buffer
 *
 * @return The parsed command
 *
 */
tp_command_t *tp_command_parse(uint8_t *buffer, size_t buffer_length);

/**
 * @brief Execute a command
 *
 * @param command The command to execute
 *
 * @return The status of the command execution
 *
 */
sl_status_t tp_command_execute(tp_command_t command, wius_tcp_server_message_t *msg);

/**
 * @brief Parse and execute a command from a buffer
 *
 * @param buffer The buffer containing the command
 * @param buffer_length The length of the buffer
 * @param msg The TCP message metadata
 *
 * @return The status of the command execution
 *
 * @note This function is a wrapper around @ref tp_parse_command and @ref tp_execute_command
 *
 */
sl_status_t tp_command_parse_and_execute(uint8_t *buffer, size_t buffer_length, wius_tcp_server_message_t *msg);