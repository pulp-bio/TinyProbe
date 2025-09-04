/**
 * @file tp_fpga.c
 *
 * @brief FPGA driver for TinyProbe source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
 *
 */

#include "tp_fpga.h"

#include "wius_spi.h"

// Number of registers to configure to defaults on startup
#define TP_NUM_DEFAULT_REGS 10

// Default register values at startup
uint32_t default_values[TP_NUM_DEFAULT_REGS] = {
    // Configure the PLL settings.
    // All clocks mux are in default (low frequency) position
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

sl_status_t tp_fpga_read_fifo(uint8_t *tx_buf, uint8_t *rx_buf, uint32_t len, bool wait)
{
    sl_status_t status = SL_STATUS_OK;

    tx_buf[0] = SP_RD_FIFO;
    tx_buf[1] = SPI_DUMMY_ADDR;

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, len, wait));

    return status;
}

sl_status_t tp_fpga_write_reg(uint32_t reg_value, uint8_t reg_addr, uint8_t *answer)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[8];
    uint8_t rx_buf[8];

    tx_buf[0] = SPI_WR_FIFO;
    tx_buf[1] = SPI_DUMMY_ADDR;
    tx_buf[2] = MEM_CTRL_WR_CMD;
    tx_buf[3] = reg_addr;
    memcpy(tx_buf + 4, &reg_value, 4);
    *answer = 0;

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 8, true));

    *answer = rx_buf[2];

    return status;
}

sl_status_t tp_fpga_send_read_reg_cmd(uint8_t reg_addr)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[8];
    uint8_t rx_buf[8];

    tx_buf[0] = SPI_WR_FIFO;
    tx_buf[1] = SPI_DUMMY_ADDR;
    tx_buf[2] = MEM_CTRL_RD_CMD;
    tx_buf[3] = reg_addr;
    memset(tx_buf + 4, 0, 4);

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 8, true));

    return status;
}

sl_status_t tp_fpga_write_reg_safe(uint32_t reg_value, uint8_t reg_addr)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t answer = 0;
    static uint8_t tx_buf[8 + 2];
    static uint8_t rx_buf[8 + 2];

    CHECK_STATUS(tp_fpga_write_reg(reg_value, reg_addr, &answer));

    CHECK_STATUS(tp_fpga_write_reg(0, 0, &answer));

    CHECK_STATUS(tp_fpga_read_fifo(tx_buf, rx_buf, 8 + 2, true));

    CHECK_STATUS(tp_fpga_send_read_reg_cmd(reg_addr));

    CHECK_STATUS(tp_fpga_read_fifo(tx_buf, rx_buf, 8 + 2, true));

    uint32_t reg_value_result = *((uint32_t *)(rx_buf + 2));

    if (reg_value != reg_value_result)
    {
        LOG_E("Expected 0x%08lX, got 0x%08lX", reg_value, reg_value_result);
        return SL_STATUS_FAIL;
    }

    return status;
}

sl_status_t tp_fpga_write_cfg(uint8_t value)
{
    sl_status_t status = SL_STATUS_OK;
    static uint8_t tx_buf[2];
    static uint8_t rx_buf[2];

    tx_buf[0] = SPI_WRITE_CFG;
    tx_buf[1] = value;

    status = wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 2, true);
    if (SL_STATUS_OK != status)
    {
        LOG_E("SPI CFG write failed!");
        return status;
    }

    return status;
}

sl_status_t tp_fpga_read_cfg(uint8_t *value)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[3];
    uint8_t rx_buf[3];

    tx_buf[0] = SPI_READ_CFG;
    tx_buf[1] = SPI_DUMMY_ADDR;
    tx_buf[2] = 0;
    *value = 0;

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    *value = rx_buf[2];

    return status;
}

sl_status_t tp_fpga_send_cmd(uint8_t cmd, uint8_t *answer)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[3];
    uint8_t rx_buf[3];

    tx_buf[0] = SPI_WR_FIFO;
    tx_buf[1] = SPI_DUMMY_ADDR;
    tx_buf[2] = cmd;
    *answer = 0;

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    *answer = rx_buf[2];

    return status;
}

sl_status_t tp_fpga_init(void)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t answer = 0;

    CHECK_STATUS(tp_fpga_write_cfg(6));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    CHECK_STATUS(tp_fpga_read_cfg(&answer));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    if ((answer & 0b111) != 6)
    {
        LOG_W("CFG reg expected 6, got %u", (answer & 0b111));
        return SL_STATUS_BUS_ERROR;
    }

    for (uint8_t i = 0; i < TP_NUM_DEFAULT_REGS; i++)
    {
        CHECK_STATUS(tp_fpga_write_reg_safe(default_values[i], default_registers[i]));
        delay_ns(TP_FPGA_SPI_DELAY_NS);
        // delay_ms(10);
    }

    return status;
}

sl_status_t tp_fpga_trigger_shot(void)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t answer = 0;

    CHECK_STATUS(tp_fpga_write_reg(SYS_CTRL_CMD_RESET, 0, &answer));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    CHECK_STATUS(tp_fpga_write_reg(SYS_CTRL_CMD_START, 0, &answer));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    delay_ms(3);
    CHECK_STATUS(tp_fpga_write_reg(SYS_CTRL_CMD_RD_EN, 0, &answer));
    delay_ns(2400);

    return status;
}

sl_status_t tp_fpga_send_start(void)
{
    uint8_t answer = 0;

    return tp_fpga_write_reg(SYS_CTRL_CMD_START, 0, &answer);
}

sl_status_t tp_fpga_reset_multififo(void)
{
    uint8_t answer = 0;

    return tp_fpga_write_reg(SYS_CTRL_CMD_RESET, 0, &answer);
}

sl_status_t tp_fpga_empty_tx(void)
{
    uint8_t tx_buf[8 + 2] = {0};
    uint8_t rx_buf[8 + 2] = {0};

    return tp_fpga_read_fifo(tx_buf, rx_buf, 8 + 2, true);
}

sl_status_t tp_fpga_en_read(void)
{
    uint8_t answer = 0;

    return tp_fpga_write_reg(SYS_CTRL_CMD_RD_EN, 0, &answer);
}