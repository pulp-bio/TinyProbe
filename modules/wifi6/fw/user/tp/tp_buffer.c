/**
 * @file tp_buffer.c
 *
 * @brief Buffer handler for TinyProbe source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
 *
 */

#include "tp_buffer.h"

void tp_buffer_init(tp_buffer_t *buf)
{
    memset(buf->slots, 0, sizeof(buf->slots));

    buf->head = 0;
    buf->tail = 0;
    buf->count = 0;

    for (size_t i = 0; i < TP_BUFFER_NUM; i++)
    {
        buf->slots[i].status = TP_BUFFER_FREE;
        buf->slots[i].length = TP_BUFFER_SIZE;
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
    if (buf->count == 0)
    {
        return NULL;
    }

    tp_buffer_slot_t *slot = &buf->slots[buf->head];
    if (slot->status != TP_BUFFER_FILLED)
    {
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
    }

    if (slot)
    {
        slot = NULL;
    }
}