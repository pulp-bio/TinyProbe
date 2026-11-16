/**
 * @file tp_fpga.c
 *
 * @brief TinyProbe FPGA driver source file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 * @author Federico Villani, ETH Zurich
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

#include "tp_fpga.h"

#include "wius_spi.h"

#define TP_FPGA_DUAL_SPI_WRITE_CMD 0x32U
#define TP_FPGA_DUAL_SPI_READ_CMD 0x4CU
#define TP_FPGA_DUAL_SPI_STREAM_READ_CMD 0x6BU
#define TP_FPGA_STATUS_REG_ADDR 15U
#define TP_FPGA_DUAL_SPI_PAYLOAD_BYTES 4U
#define TP_FPGA_DUAL_SPI_READ_DUMMY_CLKS 10U
#define TP_FPGA_DUAL_SPI_RX_SAMPLE_DELAY 0U
#define TP_FPGA_DUAL_SPI_CS_SETTLE_MS 10U
#define TP_FPGA_DUAL_SPI_WRITE_TIMEOUT_MS 100U
#define TP_FPGA_DUAL_SPI_TRANSFER_TIMEOUT_MS 1000U
#define TP_FPGA_DUAL_SPI_INTF_PLL_CLK 180000000UL
#define TP_FPGA_DUAL_SPI_INTF_PLL_REF_CLK 40000000UL
#define TP_FPGA_DUAL_SPI_SOC_PLL_CLK 20000000UL
#define TP_FPGA_DUAL_SPI_SOC_PLL_REF_CLK 40000000UL
#define TP_FPGA_DUAL_SPI_INTF_PLL_500_CTRL 0xD900UL
#define TP_FPGA_DUAL_SPI_SOC_PLL_MM_COUNT 0xA4UL
#define TP_FPGA_DUAL_SPI_DIVISION_FACTOR 90U

static sl_ssi_handle_t tp_fpga_dual_spi_handle = NULL;
// Command framing is retained by SSI until the shared peripheral is switched
// to the conventional TX/AFE setup.
static bool tp_fpga_dual_spi_framing_configured = false;

// Commands for User logic (System controller)
#define SYS_CTRL_CMD_START 1
#define SYS_CTRL_CMD_RESET 2
#define SYS_CTRL_CMD_RD_EN 3

// Number of registers to configure to defaults on startup
#define TP_NUM_DEFAULT_REGS 10

// Default register values at startup
uint32_t default_values[TP_NUM_DEFAULT_REGS] = {
    // Configure the PLL settings.
    // TX and AFE clock muxes are in the default (low frequency) position.
    // The FPGA core clock is fixed at 10 MHz; PLL register bit 2 is reserved.
    // PLL outputs for TX and AFE clocks are turned on
    0x00000050,
    // Enable all the channels, TX and AFE clock are permanently on
    0xC000FFFF,
    // PRF period correspond to 666 Hz (for faster sync) (900 Hz and more does not work so far)
    0x3A986420,
    0x001E01F4,
    0x00001792,
    0x00000002,
    // Double the depth compared to the previous settings
    0x000002F8,
    0x00000008,
    0x0000001E,
    // AFE and TX RST are inactive
    // AFE Global and Fast power down pins are controlled by register and set to 0.
    // TX TR_EN is controlled by FPGA and is set at 0
    0x00000054};

// Default register addresses at startup (for default_values)
uint8_t default_registers[TP_NUM_DEFAULT_REGS] = {
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10};

static sl_status_t tp_fpga_dual_spi_configure(void)
{
    wius_spi_inst_t instance = wius_spi_get_instance(WIUS_SPI_INST_0);
    if (instance.inst.ssi == NULL)
    {
        return SL_STATUS_INVALID_STATE;
    }

    // The generic SSI configuration remains standard because setting
    // SPI_TRANSFER_MODE_DUAL there makes the SI91x SDK take ownership of the
    // hardware CS pin.  GPIO 53 is deliberately firmware-owned.  The command
    // configuration below supplies the actual dual-line payload phase.
    const bool fpga_base_mode_already_active =
        (instance.config.width == 8U) &&
        (instance.config.mode == SL_SSI_PERIPHERAL_CPOL0_CPHA1) &&
        (instance.config.freq == TP_FPGA_DUAL_SPI_BAUDRATE) &&
        (instance.config.rx_sample_delay == TP_FPGA_DUAL_SPI_RX_SAMPLE_DELAY) &&
        (instance.config.transfer_mode == SPI_TRANSFER_MODE_STANDARD);

    // Program the SSI clock source on entry to an FPGA session. The baud rate
    // is set separately when selecting the FPGA's base SSI mode.
    if (!tp_fpga_dual_spi_framing_configured)
    {
        sl_ssi_clock_config_t clock_config = {
            .soc_pll_mm_count_value = TP_FPGA_DUAL_SPI_SOC_PLL_MM_COUNT,
            .intf_pll_500_control_value = TP_FPGA_DUAL_SPI_INTF_PLL_500_CTRL,
            .intf_pll_clock = TP_FPGA_DUAL_SPI_INTF_PLL_CLK,
            .intf_pll_reference_clock = TP_FPGA_DUAL_SPI_INTF_PLL_REF_CLK,
            .soc_pll_clock = TP_FPGA_DUAL_SPI_SOC_PLL_CLK,
            .soc_pll_reference_clock = TP_FPGA_DUAL_SPI_SOC_PLL_REF_CLK,
            .division_factor = TP_FPGA_DUAL_SPI_DIVISION_FACTOR,
        };

        sl_status_t status = sl_si91x_ssi_configure_clock(&clock_config);
        if (status != SL_STATUS_OK)
        {
            log_error("FPGA_REG: SSI clock configuration failed: 0x%lx", (unsigned long)status);
            return status;
        }
    }

    if (!fpga_base_mode_already_active)
    {
        wius_spi_config_t fpga_base_config = instance.config;
        fpga_base_config.width = 8U;
        fpga_base_config.mode = SL_SSI_PERIPHERAL_CPOL0_CPHA1;
        fpga_base_config.freq = TP_FPGA_DUAL_SPI_BAUDRATE;
        fpga_base_config.rx_sample_delay = TP_FPGA_DUAL_SPI_RX_SAMPLE_DELAY;
        // Command/address remain single-line through the enhanced command
        // configuration below; SSI_FRF_DUAL selects only the payload phase.
        fpga_base_config.transfer_mode = SPI_TRANSFER_MODE_STANDARD;

        sl_status_t status = wius_spi_reconfigure(WIUS_SPI_INST_0, &fpga_base_config);
        if (status != SL_STATUS_OK)
        {
            log_error("FPGA_REG: SSI switch to Mode-1 FPGA base mode failed: 0x%lx", (unsigned long)status);
            return status;
        }

        // A Mode-0/single-line user of the shared SSI peripheral invalidates
        // the enhanced command framing used by the FPGA transaction.
        tp_fpga_dual_spi_framing_configured = false;
    }

    tp_fpga_dual_spi_handle = instance.inst.ssi;
    if (!tp_fpga_dual_spi_framing_configured)
    {
        sl_si91x_ssi_set_slave_number(SSI_SLAVE_0);

        sl_status_t status = sl_si91x_ssi_command_config(tp_fpga_dual_spi_handle,
                                                          SSI_INST_LEN_8_BITS,
                                                          SSI_ADDR_LEN_24_BITS,
                                                          SSI_FRF_DUAL,
                                                          SSI_XFER_TYPE_INST_ADDR_STD);
        if (status != SL_STATUS_OK)
        {
            log_error("FPGA_REG: SSI command framing failed: 0x%lx", (unsigned long)status);
            return status;
        }

        tp_fpga_dual_spi_framing_configured = true;
    }

    return SL_STATUS_OK;
}

static sl_status_t tp_fpga_dual_spi_set_cs(bool active)
{
    sl_status_t status = wius_spi_set_cs(WIUS_SPI_INST_0, active);

    // SSI_MASTER_Send/Receive_Command_Data reject a transfer with a mode
    // fault when SER has no selected slave.  SER gates the SSI engine; GPIO 53
    // remains the physical chip-select and is asserted or released above.
    if (active && status == SL_STATUS_OK)
    {
        SSI0->SER |= (1UL << SSI_SLAVE_0);
    }
    else
    {
        SSI0->SER &= ~(1UL << SSI_SLAVE_0);
    }

    return status;
}

static sl_status_t tp_fpga_dual_spi_wait_for_idle(uint32_t timeout_ms)
{
    uint32_t start_ms = time_ms();

    while (sl_si91x_ssi_get_status(tp_fpga_dual_spi_handle).busy != 0U)
    {
        if ((time_ms() - start_ms) >= timeout_ms)
        {
            wius_spi_abort(WIUS_SPI_INST_0);
            return SL_STATUS_TIMEOUT;
        }
    }

    return SL_STATUS_OK;
}

static sl_status_t tp_fpga_dual_spi_send(const uint8_t *data, uint32_t length,
                                         uint8_t command, uint32_t address)
{
    sl_status_t status = wius_spi_clear_completion(WIUS_SPI_INST_0);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    status = tp_fpga_dual_spi_set_cs(true);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    int32_t driver_status =
        SSI_MASTER_Send_Command_Data((void *)data, length, command, address);
    if (driver_status != ARM_DRIVER_OK)
    {
        log_warn("DUALSPI_REG: write driver status=%ld", (long)driver_status);
        status = SL_STATUS_FAIL;
    }
    else
    {
        status = wius_spi_await_completion(WIUS_SPI_INST_0,
                                           TP_FPGA_DUAL_SPI_TRANSFER_TIMEOUT_MS);
        if (status == SL_STATUS_OK)
        {
            status = tp_fpga_dual_spi_wait_for_idle(TP_FPGA_DUAL_SPI_WRITE_TIMEOUT_MS);
        }
    }

    sl_status_t cs_status = tp_fpga_dual_spi_set_cs(false);
    return (status == SL_STATUS_OK) ? cs_status : status;
}

static sl_status_t tp_fpga_dual_spi_receive(uint8_t *data, uint32_t length,
                                            uint8_t command, uint32_t address,
                                            uint32_t dummy_clocks)
{
    sl_status_t status = wius_spi_clear_completion(WIUS_SPI_INST_0);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    status = tp_fpga_dual_spi_set_cs(true);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    delay_ms(TP_FPGA_DUAL_SPI_CS_SETTLE_MS);
    int32_t driver_status = SSI_MASTER_Receive_Command_Data(data, length, command, address, dummy_clocks);
    if (driver_status == ARM_DRIVER_OK)
    {
        status = wius_spi_await_completion(WIUS_SPI_INST_0,
                                           TP_FPGA_DUAL_SPI_TRANSFER_TIMEOUT_MS);
        if (status == SL_STATUS_OK)
        {
            status = tp_fpga_dual_spi_wait_for_idle(TP_FPGA_DUAL_SPI_WRITE_TIMEOUT_MS);
        }
    }
    else
    {
        log_warn("DUALSPI_REG: read driver status=%ld", (long)driver_status);
        status = SL_STATUS_FAIL;
    }
    delay_ms(TP_FPGA_DUAL_SPI_CS_SETTLE_MS);
    sl_status_t cs_status = tp_fpga_dual_spi_set_cs(false);
    return (status == SL_STATUS_OK) ? cs_status : status;
}

static uint32_t tp_fpga_dual_spi_decode_be_word(const uint8_t data[TP_FPGA_DUAL_SPI_PAYLOAD_BYTES])
{
    return ((uint32_t)data[0] << 24U) |
           ((uint32_t)data[1] << 16U) |
           ((uint32_t)data[2] << 8U) |
           (uint32_t)data[3];
}

static sl_status_t tp_fpga_reg_write(uint8_t reg_addr, uint32_t reg_value)
{
    if (reg_addr >= TP_FPGA_STATUS_REG_ADDR)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    _Alignas(uint32_t) uint8_t data[TP_FPGA_DUAL_SPI_PAYLOAD_BYTES] = {
        (uint8_t)(reg_value >> 24U),
        (uint8_t)(reg_value >> 16U),
        (uint8_t)(reg_value >> 8U),
        (uint8_t)reg_value,
    };

    sl_status_t status = tp_fpga_dual_spi_configure();
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    return tp_fpga_dual_spi_send(data, sizeof(data), TP_FPGA_DUAL_SPI_WRITE_CMD, reg_addr);
}

static sl_status_t tp_fpga_reg_read(uint8_t reg_addr, uint32_t *reg_value)
{
    if ((reg_addr > TP_FPGA_STATUS_REG_ADDR) || (reg_value == NULL))
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    _Alignas(uint32_t) uint8_t data[TP_FPGA_DUAL_SPI_PAYLOAD_BYTES] = {0};
    sl_status_t status = tp_fpga_dual_spi_configure();
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    status = tp_fpga_dual_spi_receive(data, sizeof(data), TP_FPGA_DUAL_SPI_READ_CMD,
                                      reg_addr, TP_FPGA_DUAL_SPI_READ_DUMMY_CLKS);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    *reg_value = tp_fpga_dual_spi_decode_be_word(data);
    return SL_STATUS_OK;
}

sl_status_t tp_fpga_read_reg(uint8_t reg_addr, uint32_t *reg_value)
{
    sl_status_t status = tp_fpga_reg_read(reg_addr, reg_value);
    if (status != SL_STATUS_OK)
    {
        return status;
    }
    // The first read after an address change can return the previous register.
    return tp_fpga_reg_read(reg_addr, reg_value);
}

sl_status_t tp_fpga_read_fifo(uint8_t *data, uint32_t length)
{
    if (data == NULL || length == 0U || length % TP_FPGA_DUAL_SPI_PAYLOAD_BYTES != 0U ||
        (uintptr_t)data % _Alignof(uint32_t) != 0U)
    {
        return SL_STATUS_INVALID_PARAMETER;
    }

    sl_status_t status = tp_fpga_dual_spi_configure();
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    // The stream address is currently unused by the RTL but remains a full
    // 24-bit single-line address phase, just like a 0x4C register read.
    status = tp_fpga_dual_spi_receive(data, length, TP_FPGA_DUAL_SPI_STREAM_READ_CMD,
                                      0U, TP_FPGA_DUAL_SPI_READ_DUMMY_CLKS);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    return SL_STATUS_OK;
}

sl_status_t tp_fpga_write_reg(uint32_t reg_value, uint8_t reg_addr)
{
    return tp_fpga_reg_write(reg_addr, reg_value);
}

sl_status_t tp_fpga_write_reg_safe(uint32_t reg_value, uint8_t reg_addr)
{
    sl_status_t status = tp_fpga_write_reg(reg_value, reg_addr);
    if (status != SL_STATUS_OK)
    {
        return status;
    }

    delay_ns(TP_FPGA_READBACK_TURNAROUND_DELAY_NS);
    delay_ms(1U);
    uint32_t readback = 0U;
    LOG_RET_STATUS(tp_fpga_read_reg(reg_addr, &readback));

    if (readback != reg_value)
    {
        log_error("FPGA register %u: expected 0x%08lX, got 0x%08lX",
                  (unsigned int)reg_addr, (unsigned long)reg_value, (unsigned long)readback);
        return SL_STATUS_FAIL;
    }
    return SL_STATUS_OK;
}

sl_status_t tp_fpga_init(void)
{
    sl_status_t status = SL_STATUS_OK;
    for (uint8_t i = 0; i < TP_NUM_DEFAULT_REGS; i++)
    {
        LOG_RET_STATUS(tp_fpga_write_reg_safe(default_values[i], default_registers[i]));
        delay_ms(1U);
    }
    return status;
}

sl_status_t tp_fpga_send_start(void)
{
    return tp_fpga_write_reg(SYS_CTRL_CMD_START, 0);
}

sl_status_t tp_fpga_reset_multififo(void)
{
    return tp_fpga_write_reg(SYS_CTRL_CMD_RESET, 0);
}

sl_status_t tp_fpga_en_read(void)
{
    return tp_fpga_write_reg(SYS_CTRL_CMD_RD_EN, 0);
}
