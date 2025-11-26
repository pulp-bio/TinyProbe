/**
 * @file tp_buffer.h
 *
 * @brief Buffer handler for TinyProbe
 *
 * @date 26.11.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
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

/**
 * @brief Buffer status enumeration
 *
 * @note Only used internally
 *
 */
typedef enum
{
    TP_BUFFER_FREE,   /**< Buffer is free */
    TP_BUFFER_FILLED, /**< Buffer is filled */
    TP_BUFFER_INUSE   /**< Buffer is in use */
} tp_buffer_status_t;

/**
 * @brief Buffer slot structure
 *
 */
typedef struct
{
    uint8_t data[TP_BUFFER_SIZE]; /**< Buffer data */
    size_t length;                /**< Length of the buffer data */
    tp_buffer_status_t status;    /**< Status of the buffer @warning Do not modify */
    size_t id;                    /**< ID of the slot */
} tp_buffer_slot_t;

/**
 * @brief Buffer structure
 *
 * @warning Do not modify the structure directly
 *
 */
typedef struct
{
    tp_buffer_slot_t slots[TP_BUFFER_NUM]; /**< Buffer slots */
    size_t head;                           /**< Head index */
    size_t tail;                           /**< Tail index */
    osSemaphoreId_t sem_read;              /**< Semaphore for reading */
    osSemaphoreId_t sem_write;             /**< Semaphore for writing */
} tp_buffer_t;

size_t tp_buffer_history_get(uint32_t **history);
void tp_buffer_history_reset(void);

/**
 * @brief Initialize the buffer structure
 *
 * @param buf Buffer structure to initialize
 *
 */
sl_status_t tp_buffer_init(tp_buffer_t *buf);

/**
 * @brief Claim a buffer slot for writing
 *
 * @param buf Buffer structure to claim from
 * @return Pointer to the claimed buffer slot
 *
 */
tp_buffer_slot_t *tp_buffer_claim_writing(tp_buffer_t *buf);

/**
 * @brief Return a buffer slot after writing
 *
 * @param buf Buffer structure to return to
 * @param slot Pointer to the buffer slot to return
 *
 */
tp_buffer_slot_t *tp_buffer_claim_reading(tp_buffer_t *buf);

/**
 * @brief Return a buffer slot after writing
 *
 * @param buf Buffer structure to return to
 * @param slot Pointer to the buffer slot to return
 * @param discard Discard the buffer slot after writing
 *
 */
void tp_buffer_return_writing(tp_buffer_t *buf, tp_buffer_slot_t *slot);

/**
 * @brief Return a buffer slot after reading
 *
 * @param buf Buffer structure to return to
 * @param slot Pointer to the buffer slot to return
 * @param discard Discard the buffer slot after reading
 *
 */
void tp_buffer_return_reading(tp_buffer_t *buf, tp_buffer_slot_t *slot);