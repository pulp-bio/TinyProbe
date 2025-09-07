/**
 * @file tp_afe.h
 *
 * @brief AFE driver for TinyProbe
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
 * @brief AFE test pattern enumeration
 *
 */
typedef enum tp_afe_patt
{
    NORMAL_OPERATION = 0, /**< Normal operation (No test pattern) */
    HALF_ZEROS_HALF_ONES, /**< (Sync) DIGRESx word is replaced by half 1s and half 0s (11111110000000) */
    ALTERN_ZERO_ONE,      /**< (Deskew) DIGRESx word is replaced by alternate 0s and 1s (01010101010101) */
    CUSTOM,               /**< Not supported */
    ALL_ONES,             /**< Ones in all bits (11111111111111) of DIGRESx */
    TOGGLE,               /**< All bits (11111111111111) of DIGRESx and then (00000000000000) */
    ALL_ZEROS,            /**< Zeros in all bits (00000000000000) of DIGRESx */
    RAMP                  /**< The ADCOUTx word increments every conversion clock and then decrements */
} tp_afe_patt_t;

/**
 * @brief AFE initialization
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 * @note This function must be called before any other AFE function
 *
 */
sl_status_t tp_afe_init(void);

/**
 * @brief AFE test pattern selection
 *
 * @param pattern: Test pattern to be applied
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during writing to registers
 *
 */
sl_status_t tp_afe_test_pattern(tp_afe_patt_t pattern);

/**
 * @brief Write to a register of the AFE
 *
 * @param address: Address of the register to write to
 * @param value: Value to write to the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during SPI transfer
 *
 */
sl_status_t tp_afe_write_reg(uint8_t address, uint16_t value);

/**
 * @brief Write to a register of the AFE and check if the write was successful
 *
 * @param address: Address of the register to write to
 * @param value: Value to write to the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Write was not successful
 * @retval other: Error during SPI transfer
 *
 */
sl_status_t tp_afe_write_reg_safe(uint8_t address, uint16_t value);

/**
 * @brief Write to a register of the AFE in the DTGC (Digital Time Gain Compensation) block
 *
 * @param address: Address of the register to write to
 * @param value: Value to write to the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during SPI transfer
 *
 */
sl_status_t tp_afe_write_reg_dtgc(uint8_t address, uint16_t value);

/**
 * @brief Write to a register of the AFE in the DTGC (Digital Time Gain Compensation) block and check if the write was successful
 *
 * @param address: Address of the register to write to
 * @param value: Value to write to the register
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_FAIL: Write was not successful
 * @retval other: Error during SPI transfer
 *
 */
sl_status_t tp_afe_write_reg_dtgc_safe(uint8_t address, uint16_t value);

/**
 * @brief Read from a register of the AFE
 *
 * @param address: Address of the register to read from
 * @param value: Pointer to the variable where the value of the register will be stored
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during SPI transfer
 *
 */
sl_status_t tp_afe_read_reg(uint8_t address, uint16_t *value);

/**
 * @brief Read from a register of the AFE in the DTGC (Digital Time Gain Compensation) block
 *
 * @param address: Address of the register to read from
 * @param value: Pointer to the variable where the value of the register will be stored
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during SPI transfer
 *
 */
sl_status_t tp_afe_read_reg_dtgc(uint8_t address, uint16_t *value);
