/**
 * @file tp.h
 *
 * @brief TinyProbe main header file
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

#pragma once

#include "common.h"
#include "wius_udp.h"
#include "tp_buffer.h"

extern wius_udp_t tp_socket;
extern char client_ip[16];
extern int client_port;

extern bool enable_udp_replies;
extern uint16_t n_packs_to_read;
extern uint16_t cb_pack_id;

extern osSemaphoreId_t sem_fpga;
extern osMessageQueueId_t q_wifi_tx;

extern tp_buffer_t tp_buf;

extern volatile uint32_t count_interrupt;

/**
 * @brief Initialize the FPGA (SPI, GPIOs, register values)
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: SPI, GPIO interrupt or register initialization failed
 *
 */
sl_status_t tp_init(void);

/**
 * @brief TinyProbe main thread
 *
 */
void tp_main_thread(void);