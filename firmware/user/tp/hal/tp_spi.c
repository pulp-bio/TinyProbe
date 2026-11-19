/**
 * @file tp_spi.c
 *
 * @brief TinyProbe shared SPI bus
 *
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 * @author Lisa Maria Odermatt, ETH Zurich
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

#include "tp_spi.h"

#include "wius_spi.h"
#include "sl_si91x_ssi_primary_config.h"

static wius_spi_config_t spi_fpga_config = {
    .cs_mode = WIUS_SPI_CS_SW,
    .cs_pin = WIUS_SPI_EXT_CS0,
    .cs_polarity = 0,
    .freq = WIUS_SPI_FREQ,
    // Base FPGA mode. Dual payload framing is installed by the FPGA HAL.
    // The shared SSI wrapper explicitly restores software CS ownership on
    // GPIO 53 after every mode switch.
    .mode = SL_SSI_PERIPHERAL_CPOL0_CPHA1,
    .transfer_mode = SPI_TRANSFER_MODE_STANDARD,
    .cs_assert_delay_ns = WIUS_SPI_CS_ASSERT_DELAY_NS,
    .cs_deassert_delay_ns = WIUS_SPI_CS_DEASSERT_DELAY_NS,
    .rx_sample_delay = 0U,
    .width = 8,
};

static const wius_spi_config_t spi_external_config = {
    .cs_mode = WIUS_SPI_CS_SW,
    .cs_pin = WIUS_SPI_EXT_CS0,
    .cs_polarity = 0,
    .freq = WIUS_SPI_FREQ,
    .mode = SL_SSI_PERIPHERAL_CPOL0_CPHA0,
    .transfer_mode = SPI_TRANSFER_MODE_STANDARD,
    .cs_assert_delay_ns = WIUS_SPI_CS_ASSERT_DELAY_NS,
    .cs_deassert_delay_ns = WIUS_SPI_CS_DEASSERT_DELAY_NS,
    .rx_sample_delay = 0U,
    .width = 8,
};

sl_status_t tp_spi_init(void)
{
    return wius_spi_init(WIUS_SPI_INST_0, &spi_fpga_config);
}

sl_status_t tp_spi_select(tp_mux_t target)
{
    switch (target)
    {
    case TP_MUX_AFE:
    case TP_MUX_TX:
    {
        // Reconfigure only when leaving the FPGA or otherwise changing bus settings.
        wius_spi_inst_t current = wius_spi_get_instance(WIUS_SPI_INST_0);
        if ((current.inst.ssi == NULL) ||
            (current.config.freq != spi_external_config.freq) ||
            (current.config.width != spi_external_config.width) ||
            (current.config.mode != spi_external_config.mode) ||
            (current.config.transfer_mode != spi_external_config.transfer_mode) ||
            (current.config.rx_sample_delay != spi_external_config.rx_sample_delay))
        {
            sl_status_t status = wius_spi_reconfigure(WIUS_SPI_INST_0, &spi_external_config);
            if (status != SL_STATUS_OK)
            {
                return status;
            }
        }
        break;
    }

    case TP_MUX_FPGA:
        // Each FPGA HAL transaction restores Mode 1 and dual-data framing as needed.
        break;

    case TP_MUX_PLL:
        // In PLL mode the chip-select pin controls the FPGA PLL directly.
        break;

    default:
        return SL_STATUS_INVALID_PARAMETER;
    }

    tp_mux_select(target);
    delay_ms(10);

    return SL_STATUS_OK;
}
