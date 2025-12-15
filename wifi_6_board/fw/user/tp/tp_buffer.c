/**
 * @file tp_buffer.c
 *
 * @brief Buffer handler for TinyProbe source file
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

#include "tp_buffer.h"

#include "cmsis_os2.h"

#define BUFFER_HISTORY_ENABLED 0
#define BUFFER_HISTORY_NUM_ENTRIES 1024

uint32_t buffer_history[BUFFER_HISTORY_NUM_ENTRIES] = {0};
size_t buffer_history_index = 0;

typedef enum buffer_history_event
{
    BUFFER_HISTORY_EVENT_CLAIM_WRITE = 0,
    BUFFER_HISTORY_EVENT_RETURN_WRITE = 1,
    BUFFER_HISTORY_EVENT_CLAIM_READ = 2,
    BUFFER_HISTORY_EVENT_RETURN_READ = 3,
} buffer_history_event_t;

inline static void buffer_history_record(buffer_history_event_t event, uint8_t buffer_index)
{
#if BUFFER_HISTORY_ENABLED
    buffer_history[buffer_history_index] = (osKernelGetTickCount() & 0xFFFF) | (event << 24) | (buffer_index << 16);
    buffer_history_index = (buffer_history_index + 1) % BUFFER_HISTORY_NUM_ENTRIES;
#else
    UNUSED(event);
    UNUSED(buffer_index);
#endif
}

size_t tp_buffer_history_get(uint32_t **history)
{
    *history = buffer_history;
    return buffer_history_index;
}

void tp_buffer_history_reset(void)
{
    buffer_history_index = 0;
    memset(buffer_history, 0, sizeof(buffer_history));
}

sl_status_t tp_buffer_init(tp_buffer_t *buf)
{
    buf->sem_read = osSemaphoreNew(TP_BUFFER_NUM, 0, NULL);
    if (buf->sem_read == NULL)
    {
        LOG_E("Failed to create read semaphore");
        return SL_STATUS_FAIL;
        ;
    }

    buf->sem_write = osSemaphoreNew(TP_BUFFER_NUM, TP_BUFFER_NUM, NULL);
    if (buf->sem_write == NULL)
    {
        LOG_E("Failed to create write semaphore");
        return SL_STATUS_FAIL;
    }

    memset(buf->slots, 0, sizeof(buf->slots));

    buf->head = 0;
    buf->tail = 0;

    for (size_t i = 0; i < TP_BUFFER_NUM; i++)
    {
        buf->slots[i].status = TP_BUFFER_FREE;
        buf->slots[i].length = TP_BUFFER_SIZE;
        buf->slots[i].id = i;
    }

    memset(buffer_history, 0, sizeof(buffer_history));

    return SL_STATUS_OK;
}

tp_buffer_slot_t *tp_buffer_claim_writing(tp_buffer_t *buf)
{
    osStatus_t status;

    // Wait for a free slot
    status = osSemaphoreAcquire(buf->sem_write, 1000);
    if (status != osOK)
    {
        // LOG_W("Failed to acquire write semaphore for buffer: %d", status);
        return NULL;
    }

    tp_buffer_slot_t *slot = &buf->slots[buf->tail];
    if (slot->status != TP_BUFFER_FREE)
    {
        LOG_W("Buffer slot not free when claiming for writing");
        osSemaphoreRelease(buf->sem_write);
        return NULL;
    }

    buffer_history_record(BUFFER_HISTORY_EVENT_CLAIM_WRITE, buf->tail);

    slot->status = TP_BUFFER_INUSE;
    buf->tail = (buf->tail + 1) % TP_BUFFER_NUM;

    return slot;
}

tp_buffer_slot_t *tp_buffer_claim_reading(tp_buffer_t *buf)
{
    osStatus_t status;

    status = osSemaphoreAcquire(buf->sem_read, osWaitForever);
    if (status != osOK)
    {
        LOG_W("Failed to acquire read semaphore for buffer: %d", status);
        return NULL;
    }

    tp_buffer_slot_t *slot = &buf->slots[buf->head];
    if (slot->status != TP_BUFFER_FILLED)
    {
        LOG_W("Buffer slot not filled when claiming for reading");
        osSemaphoreRelease(buf->sem_read);
        return NULL;
    }

    buffer_history_record(BUFFER_HISTORY_EVENT_CLAIM_READ, buf->head);

    slot->status = TP_BUFFER_INUSE;

    return slot;
}

void tp_buffer_return_writing(tp_buffer_t *buf, tp_buffer_slot_t *slot)
{
    buffer_history_record(BUFFER_HISTORY_EVENT_RETURN_WRITE, slot->id);

    slot->status = TP_BUFFER_FILLED;

    osSemaphoreRelease(buf->sem_read);

    slot = NULL;

    // osThreadYield();
}

void tp_buffer_return_reading(tp_buffer_t *buf, tp_buffer_slot_t *slot)
{
    buffer_history_record(BUFFER_HISTORY_EVENT_RETURN_READ, slot->id);

    buf->head = (buf->head + 1) % TP_BUFFER_NUM;
    slot->length = TP_BUFFER_SIZE;
    slot->status = TP_BUFFER_FREE;

    osSemaphoreRelease(buf->sem_write);

    slot = NULL;

    osThreadYield();
}