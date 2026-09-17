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
 * @brief Get SPI instance by ID
 *
 * @param id: SPI instance ID
 *
 * @return SPI instance configuration and driver handle
 *
 */
wius_spi_inst_t wius_spi_get_instance(uint8_t id);

/**
 * @brief Initialize SPI module
 *
 * @param id: SPI instance to initialize
 * @param config: Pointer to the SPI configuration
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_INVALID_PARAMETER: Invalid instance
 * @retval other: Error during peripheral initialization
 *
 */
sl_status_t wius_spi_init(uint8_t id, wius_spi_config_t *config);
/** Reconfigure the already initialized SSI peripheral without changing its CS GPIO ownership. */
sl_status_t wius_spi_reconfigure(uint8_t id, const wius_spi_config_t *config);
sl_status_t wius_spi_set_cs(uint8_t id, bool active);

/**
 * @brief Transfer data over SPI
 *
 * @param id: SPI instance to use for transfer
 * @param tx_buf: Pointer to the buffer containing the data to be sent
 * @param rx_buf: Pointer to the buffer where the received data will be stored
 * @param len: Number of bytes to transfer
 * @param wait: Wait for transfer to complete
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: Error during transfer or waiting
 *
 */
sl_status_t wius_spi_xfer(uint8_t id, uint8_t *tx_buf, uint8_t *rx_buf, size_t len, bool wait);

/** Send data over SPI. This entry point is also used by the AFE and TX drivers. */
sl_status_t wius_spi_send(uint8_t id, const uint8_t *tx_buf, size_t len, bool wait);

/**
 * @brief Await SPI transfer completion
 *
 * @param id: SPI instance to await
 *
 * @retval SL_STATUS_OK: Success
 * @retval SL_STATUS_TIMEOUT: The transfer timed out
 * @retval SL_STATUS_FAIL: Error during acquiring semaphores
 *
 */
sl_status_t wius_spi_await(uint8_t id);

/** Remove any pending completion event before starting a direct SSI transfer. */
sl_status_t wius_spi_clear_completion(uint8_t id);

/** Wait for a direct SSI transfer callback without changing chip select. */
sl_status_t wius_spi_await_completion(uint8_t id, uint32_t timeout_ms);

/** Abort the current SSI transfer before releasing its buffers. */
void wius_spi_abort(uint8_t id);
