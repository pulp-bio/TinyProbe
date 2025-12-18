/**
 * @file tp_command_writefpga.c
 *
 * @brief TinyProbe FPGA write command implementation file
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

#include "tp_command_writefpga.h"

#include "tp_fpga.h"

sl_status_t tp_write_fpga(uint8_t *args, uint16_t args_length)
{
    LOG_D("Executing");

    UNUSED(args_length);
    sl_status_t status = SL_STATUS_OK;

    uint8_t fpga_reg_addr = GET(args, uint8_t, 0);
    uint32_t fpga_reg_value = GET(args, uint32_t, 1);

    LOG_D("Writing %lu to %u", fpga_reg_value, fpga_reg_addr);

    CHECK_STATUS(tp_fpga_write_reg_safe(fpga_reg_value, fpga_reg_addr));

    LOG_D("Done");

    return SL_STATUS_OK;
}