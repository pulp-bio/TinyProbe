/**
 * @file tp.h
 *
 * @brief TinyProbe main header file
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

/**
 * @brief Initialize the FPGA (SPI, GPIOs, register values)
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: SPI, GPIO interrupt or register initialization failed
 *
 */
sl_status_t tp_init(void);
void tp_main_thread(void);

sl_status_t tp_ping(uint8_t *args, uint16_t args_length);
sl_status_t tp_en_replies(uint8_t *args, uint16_t args_length);
sl_status_t tp_sw_mux(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_spi(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_fpga(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_afe(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_tx(uint8_t *args, uint16_t args_length);
sl_status_t tp_delay_ns(uint8_t *args, uint16_t args_length);
sl_status_t tp_sleep_ms(uint8_t *args, uint16_t args_length);
sl_status_t tp_ctrl_pwr(uint8_t *args, uint16_t args_length);
sl_status_t tp_trigger_shot(uint8_t *args, uint16_t args_length);