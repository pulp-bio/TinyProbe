/**
 * @file tp_fpga.h
 *
 * @brief FPGA driver for TinyProbe
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

// Generic commands
#define SPI_READ_CFG 1
#define SPI_WRITE_CFG 2
#define SP_RD_FIFO 16
#define SPI_WR_FIFO 17

#define SPI_DUMMY_ADDR 0

#define SPI_BURST_MODE_SIZE 1000

// Commands for User logic (System controller)
#define SYS_CTRL_CMD_DUMMY 0
#define SYS_CTRL_CMD_START 1
#define SYS_CTRL_CMD_RESET 2
#define SYS_CTRL_CMD_RD_EN 3
#define SYS_CTRL_CMD_ECHO 4

// Commands for Memory Controller
#define MEM_CTRL_WR_CMD 1
#define MEM_CTRL_RD_CMD 0

/**
 * @brief FPGA initialization
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 * @note This function must be called before any other FPGA function
 *
 */
sl_status_t tp_fpga_init(void);

/**
 * @brief Write to a register of the FPGA
 *
 * @param reg_value: Value to write to the register
 * @param reg_addr: Address of the register to write to
 * @param answer: Pointer to the answer buffer
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_fpga_write_reg(uint32_t reg_value, uint8_t reg_addr, uint8_t *answer);

/**
 * @brief Write to a register of the FPGA and check if the write was successful
 *
 * @param reg_value: Value to write to the register
 * @param reg_addr: Address of the register to write to
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Write was not successful
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_fpga_write_reg_safe(uint32_t reg_value, uint8_t reg_addr);

/**
 * @brief Write to the configuration register of the FPGA
 *
 * @param value: Value to write to the configuration register
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_fpga_write_cfg(uint8_t value);

/**
 * @brief Send a read register command to the FPGA
 *
 * @param reg_addr: Address of the register to read
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_fpga_send_read_reg_cmd(uint8_t reg_addr);

/**
 * @brief Read from the FIFO of the FPGA
 *
 * @param tx_buf: Buffer to write to the FIFO
 * @param rx_buf: Buffer to read from the FIFO
 * @param len: Length of the buffer
 * @param wait: Wait for the transfer to finish
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during reading from the FIFO
 *
 */
sl_status_t tp_fpga_read_fifo(uint8_t *tx_buf, uint8_t *rx_buf, uint32_t len, bool wait);

/**
 * @brief Read from the configuration register of the FPGA
 *
 * @param value: Pointer to the value buffer
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during reading from the register
 *
 */
sl_status_t tp_fpga_read_cfg(uint8_t *value);

/**
 * @brief Send a command to the FPGA
 *
 * @param cmd: Command to send
 * @param answer: Pointer to the answer buffer
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during sending the command
 *
 */
sl_status_t tp_fpga_send_cmd(uint8_t cmd, uint8_t *answer);

/**
 * @brief Trigger a shot on the FPGA
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during triggering the shot
 *
 */
sl_status_t tp_fpga_trigger_shot(void);

/**
 * @brief Send a start command to the FPGA
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during sending the command
 *
 */
sl_status_t tp_fpga_send_start(void);

/**
 * @brief Reset the FIFO of the FPGA
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during resetting the FIFO
 *
 */
sl_status_t tp_fpga_reset_multififo(void);

/**
 * @brief Empty the TX FIFO of the FPGA
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during emptying the TX FIFO
 *
 */
sl_status_t tp_fpga_empty_tx(void);

/**
 * @brief Enable the readout of the FPGA
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during enabling the readout
 *
 */
sl_status_t tp_fpga_en_read(void);