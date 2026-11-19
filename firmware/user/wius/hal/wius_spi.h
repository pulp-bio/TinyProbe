/**
 * @file wius_spi.h
 *
 * @brief WiUS SPI implementation header file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Lisa Maria Odermatt, ETH Zurich
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

#include "sl_si91x_ssi.h"

#include "wius_gpio.h"

#define WIUS_SPI_INST_0 0 /**< Instance 0 on pins [25, 26, 27, 53] (SSI Master) */
#define WIUS_SPI_INST_1 1 /**< Reserved */

/**
 * @brief SPI chip select modes enumeration
 *
 */
typedef enum wius_spi_cs_mode
{
    WIUS_SPI_CS_NONE = 0, /**< No chip select */
    WIUS_SPI_CS_SW = 1,   /**< Software controlled chip select (Handled by this API) */
    WIUS_SPI_CS_HW = 2    /**< Hardware controlled chip select (Handled by peripheral) */
} wius_spi_cs_mode_t;

/**
 * @brief SPI instance configuration
 *
 */
typedef struct wius_spi_config
{
    uint8_t width;              /**< Data width in bits */
    uint32_t mode;              /**< SSI clock mode */
    uint32_t freq;              /**< Clock frequency in Hz */
    uint32_t transfer_mode;     /**< SSI transfer mode */
    uint32_t cs_assert_delay_ns; /**< Delay after CS assert before transfer start */
    uint32_t cs_deassert_delay_ns; /**< Delay before CS deassert after transfer completion */
    uint8_t rx_sample_delay;    /**< SSI receive sample delay */
    wius_spi_cs_mode_t cs_mode; /**< Chip select mode */
    uint8_t cs_pin;             /**< Chip select pin (only for SW mode) */
    uint8_t cs_polarity;        /**< Chip select polarity (only for SW mode, 0 for active low, 1 for active high) */
} wius_spi_config_t;

/**
 * @brief SPI instance enumeration
 *
 */
typedef struct wius_spi_inst
{
    uint8_t id;               /**< Instance ID */
    wius_spi_config_t config; /**< Configuration */
    wius_gpio_t cs;           /**< Chip select GPIO (only in SW/HW mode) */

    union instance /**< Peripheral handle union */
    {
        sl_ssi_handle_t ssi; /**< Peripheral handle (SSI) */
    } inst;                    /**< Peripheral handle */
} wius_spi_inst_t;

/**
 * @brief Get a snapshot of the active SPI configuration and SSI handle.
 *
 * @param[in] id SPI instance ID.
 * @return Instance snapshot or an empty instance for an unsupported ID.
 */
wius_spi_inst_t wius_spi_get_instance(uint8_t id);

/**
 * @brief Initialize an SSI peripheral and its chip select.
 *
 * @param[in] id SPI instance ID.
 * @param[in] config Initial bus and chip-select settings.
 * @retval SL_STATUS_OK Initialization completed.
 * @return An error if the instance, settings, or peripheral initialization failed.
 */
sl_status_t wius_spi_init(uint8_t id, wius_spi_config_t *config);

/**
 * @brief Reconfigure an initialized SSI peripheral while retaining its chip-select GPIO.
 *
 * @param[in] id SPI instance ID.
 * @param[in] config New SSI settings. Preserve the existing chip-select assignment.
 * @return SL_STATUS_OK on success or an SSI configuration error.
 */
sl_status_t wius_spi_reconfigure(uint8_t id, const wius_spi_config_t *config);

/**
 * @brief Assert or release software chip select for a caller-managed transfer.
 *
 * @param[in] id SPI instance ID.
 * @param[in] active True to assert chip select, false to release it.
 * @return SL_STATUS_OK on success or an instance or driver error.
 */
sl_status_t wius_spi_set_cs(uint8_t id, bool active);

/**
 * @brief Start a full-duplex SPI transfer with chip select managed by this driver.
 *
 * @param[in] id SPI instance ID.
 * @param[in] tx_buf Bytes to transmit.
 * @param[out] rx_buf Buffer for received bytes.
 * @param[in] len Number of bytes to transfer.
 * @param[in] wait True to wait for completion and release chip select.
 * @return SL_STATUS_OK on success or a setup, transfer, or timeout error.
 * @note If wait is false, call wius_spi_await() before reusing either buffer.
 */
sl_status_t wius_spi_xfer(uint8_t id, uint8_t *tx_buf, uint8_t *rx_buf, size_t len, bool wait);

/**
 * @brief Start a transmit-only SPI transfer with chip select managed by this driver.
 *
 * @param[in] id SPI instance ID.
 * @param[in] tx_buf Bytes to transmit.
 * @param[in] len Number of bytes to send.
 * @param[in] wait True to wait for completion and release chip select.
 * @return SL_STATUS_OK on success or a setup, transfer, or timeout error.
 * @note If wait is false, call wius_spi_await() before reusing the transmit buffer.
 */
sl_status_t wius_spi_send(uint8_t id, const uint8_t *tx_buf, size_t len, bool wait);

/**
 * @brief Finish a transfer started by wius_spi_xfer() or wius_spi_send().
 *
 * Waits up to one second, aborts on a wait error, and releases chip select
 * after the configured deassertion delay.
 *
 * @param[in] id SPI instance ID.
 * @retval SL_STATUS_OK The completion event was received.
 * @retval SL_STATUS_TIMEOUT The transfer timed out.
 * @return An error for an invalid instance or a failed semaphore wait.
 */
sl_status_t wius_spi_await(uint8_t id);

/**
 * @brief Discard stale completion events before starting a caller-managed SSI transfer.
 *
 * @param[in] id SPI instance ID.
 * @return SL_STATUS_OK if the completion semaphore was drained.
 */
sl_status_t wius_spi_clear_completion(uint8_t id);

/**
 * @brief Wait for a caller-managed SSI transfer to signal completion.
 *
 * The caller owns chip select and any peripheral-idle check. If the wait
 * fails, the driver requests a transfer abort before returning.
 *
 * @param[in] id SPI instance ID.
 * @param[in] timeout_ms Timeout in milliseconds.
 * @retval SL_STATUS_OK The completion event was received.
 * @retval SL_STATUS_TIMEOUT The timeout elapsed.
 * @return An error for an invalid instance or a failed semaphore wait.
 */
sl_status_t wius_spi_await_completion(uint8_t id, uint32_t timeout_ms);

/**
 * @brief Request cancellation of an active SSI transfer before reusing its buffers.
 *
 * @param[in] id SPI instance ID.
 */
void wius_spi_abort(uint8_t id);
