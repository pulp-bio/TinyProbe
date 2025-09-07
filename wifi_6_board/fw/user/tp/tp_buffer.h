/**
 * @file tp_buffer.h
 *
 * @brief Buffer handler for TinyProbe
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
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
    size_t count;                          /**< Number of filled slots */
} tp_buffer_t;

/**
 * @brief Initialize the buffer structure
 *
 * @param buf Buffer structure to initialize
 *
 */
void tp_buffer_init(tp_buffer_t *buf);

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
 * @brief Return a buffer slot after reading
 *
 * @param buf Buffer structure to return to
 * @param slot Pointer to the buffer slot to return
 * @param discard Discard the buffer slot after reading
 *
 */
void tp_buffer_return(tp_buffer_t *buf, tp_buffer_slot_t *slot, bool discard);