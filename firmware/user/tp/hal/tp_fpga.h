/**
 * @file tp_fpga.h
 *
 * @brief TinyProbe FPGA driver header file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 * @author Lisa Maria Odermatt, ETH Zurich
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

/** Initialize and verify the FPGA configuration registers. */
sl_status_t tp_fpga_init(void);

/** Write a 32-bit FPGA register using 0x32. */
sl_status_t tp_fpga_write_reg(uint32_t reg_value, uint8_t reg_addr);

/** Write a 32-bit FPGA register and verify its readback. */
sl_status_t tp_fpga_write_reg_safe(uint32_t reg_value, uint8_t reg_addr);

/** Read a 32-bit FPGA register using 0x4C. */
sl_status_t tp_fpga_read_reg(uint8_t reg_addr, uint32_t *reg_value);

/** Read whole 32-bit stream words using 0x6B. The receive buffer must be DMA-aligned. */
sl_status_t tp_fpga_read_fifo(uint8_t *data, uint32_t length);

/** Start an acquisition or arm the FPGA for external triggers. */
sl_status_t tp_fpga_send_start(void);

/** Reset the acquisition FIFOs. */
sl_status_t tp_fpga_reset_multififo(void);

/** Start moving the captured data to the SPI stream FIFO. */
sl_status_t tp_fpga_en_read(void);
