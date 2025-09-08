/**
 * @file tp_command.c
 *
 * @brief Command handler for TinyProbe source file
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

#include "tp_command.h"

#include "tp.h"

tp_command_t _tp_command_commands[TP_COMMAND_MAX];
uint16_t _tp_num_commands = 0;

// Command packet minimum lengths
uint8_t _tp_command_min_lengths[TP_CMD_ID_MAX] = {0, 1, 1, 1, 5, 4, 6, 8, 4, 2, 6};

tp_command_t *tp_command_parse(uint8_t *buffer, size_t buffer_length)
{
    (void)buffer_length;

    // clear the commands
    memset(_tp_command_commands, 0, sizeof(_tp_command_commands));
    _tp_num_commands = 0;

    // get number of commands (byte 0,1)
    uint16_t num_commands = *((uint16_t *)&buffer[0]);

    if (num_commands > TP_COMMAND_MAX || num_commands == 0)
    {
        LOG_W("%u is invalid amount of commands (0 - %u)", 0, TP_COMMAND_MAX);
        return NULL;
    }

    // index of the first command
    uint16_t index = 2;

    // iterate over the commands
    for (uint16_t i = 0; i < num_commands; i++)
    {
        // get the command id (offset byte 0)
        tp_command_id_t id = buffer[index];
        index++;

        if (id >= TP_CMD_ID_MAX)
        {
            LOG_W("%u is invalid, max. valid is %u", id, TP_CMD_ID_MAX);
            return NULL;
        }

        // get the command arguments length (offset byte 1,2)
        uint16_t length = *((uint16_t *)&buffer[index]);
        index += 2;

        // get the command arguments
        uint8_t *args = &buffer[index];
        index += length;

        // create the command
        tp_command_t command = {
            .id = id,
            .args_length = length,
            .args = args};

        //        LOG_D("  %u: %u", id, length);
        //        for (uint8_t j = 0; j < length; j++)
        //        {
        //          LOG_D("    %u", args[j]);
        //        }

        // store the command
        _tp_command_commands[i] = command;

        // increment the number of commands
        _tp_num_commands++;
    }

    return _tp_command_commands;
}

sl_status_t tp_command_execute(tp_command_t command)
{
    if (command.args_length < _tp_command_min_lengths[command.id])
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    // LOG_D("Executing command with ID %d", command.id);

    switch (command.id)
    {
    case TP_CMD_PING:
        tp_ping(command.args, command.args_length);
        break;
    case TP_CMD_EN_REPLIES:
        tp_en_replies(command.args, command.args_length);
        break;
    case TP_CMD_SW_MUX:
        tp_sw_mux(command.args, command.args_length);
        break;
    case TP_CMD_WRITE_SPI:
        tp_write_spi(command.args, command.args_length);
        break;
    case TP_CMD_WRITE_FPGA:
        tp_write_fpga(command.args, command.args_length);
        break;
    case TP_CMD_WRITE_AFE:
        tp_write_afe(command.args, command.args_length);
        break;
    case TP_CMD_WRITE_TX:
        tp_write_tx(command.args, command.args_length);
        break;
    case TP_CMD_DELAY_NS:
        tp_delay_ns(command.args, command.args_length);
        break;
    case TP_CMD_SLEEP_MS:
        tp_sleep_ms(command.args, command.args_length);
        break;
    case TP_CMD_CTRL_PWR:
        tp_ctrl_pwr(command.args, command.args_length);
        break;
    case TP_CMD_TRIGGER_SHOT:
        tp_trigger_shot(command.args, command.args_length);
        break;
    default:
        LOG_W("Unknown command");
        return SL_STATUS_INVALID_PARAMETER;
    }
    return SL_STATUS_OK;
}

sl_status_t tp_command_parse_and_execute(uint8_t *buffer, size_t buffer_length)
{
    sl_status_t status = SL_STATUS_OK;
    tp_command_t *commands = tp_command_parse(buffer, buffer_length);

    for (uint16_t i = 0; i < _tp_num_commands; i++)
    {
        CHECK_STATUS(tp_command_execute(commands[i]));
    }

    return SL_STATUS_OK;
}