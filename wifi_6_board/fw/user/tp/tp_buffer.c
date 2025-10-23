/**
 * @file tp_buffer.c
 *
 * @brief Buffer handler for TinyProbe source file
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

#include "tp_buffer.h"

#include "cmsis_os2.h"

osSemaphoreId_t sem_tp_buffer_new = NULL;

sl_status_t tp_buffer_init(tp_buffer_t *buf)
{
    sem_tp_buffer_new = osSemaphoreNew(TP_BUFFER_NUM, 0, NULL);
    if (sem_tp_buffer_new == NULL)
    {
        LOG_E("Error creating TP buffer semaphore");
        return SL_STATUS_FAIL;
    }

    tp_buffer_reset(buf);

    return SL_STATUS_OK;
}

void tp_buffer_reset(tp_buffer_t *buf)
{
    memset(buf->slots, 0, sizeof(buf->slots));

    buf->head = 0;
    buf->tail = 0;
    buf->count = 0;

    for (size_t i = 0; i < TP_BUFFER_NUM; i++)
    {
        buf->slots[i].status = TP_BUFFER_FREE;
        buf->slots[i].length = TP_BUFFER_SIZE;
        buf->slots[i].id = i;
    }

    if (sem_tp_buffer_new != NULL)
    {
        while (osSemaphoreAcquire(sem_tp_buffer_new, 0) == osOK)
            ;
    }
}

tp_buffer_slot_t *tp_buffer_claim_writing(tp_buffer_t *buf)
{
    if (buf->count >= TP_BUFFER_NUM)
    {
        return NULL;
    }

    tp_buffer_slot_t *slot = &buf->slots[buf->tail];
    if (slot->status != TP_BUFFER_FREE)
    {
        return NULL;
    }

    slot->status = TP_BUFFER_INUSE;
    buf->tail = (buf->tail + 1) % TP_BUFFER_NUM;

    return slot;
}

tp_buffer_slot_t *tp_buffer_claim_reading(tp_buffer_t *buf)
{
    // if (buf->count == 0)
    // {
    //     return NULL;
    // }
    osStatus_t status;
    status = osSemaphoreAcquire(sem_tp_buffer_new, osWaitForever);
    if (status != osOK)
    {
        LOG_W("Failed to acquire semaphore for buffer: %d", status);
        LOG_W("Semaphore: %p", sem_tp_buffer_new);
        return NULL;
    }

    tp_buffer_slot_t *slot = &buf->slots[buf->head];
    if (slot->status != TP_BUFFER_FILLED)
    {
        LOG_W("Buffer slot not filled when claiming for reading");
        return NULL;
    }

    slot->status = TP_BUFFER_INUSE;

    return slot;
}

void tp_buffer_return(tp_buffer_t *buf, tp_buffer_slot_t *slot, bool discard)
{
    if (slot)
    {
        slot->status = discard ? TP_BUFFER_FREE : TP_BUFFER_FILLED;
    }

    if (discard)
    {
        buf->count--;
        buf->head = (buf->head + 1) % TP_BUFFER_NUM;
        slot->length = TP_BUFFER_SIZE;
    }
    else
    {
        buf->count++;
        osSemaphoreRelease(sem_tp_buffer_new);
    }

    if (slot)
    {
        slot = NULL;
    }
}