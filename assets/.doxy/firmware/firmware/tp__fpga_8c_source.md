

# File tp\_fpga.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**tp**](dir_79b6053a5ce46efc48854f71c67386da.md) **>** [**hal**](dir_ba257e9fe5d1efafb020d894779bedf8.md) **>** [**tp\_fpga.c**](tp__fpga_8c.md)

[Go to the documentation of this file](tp__fpga_8c.md)


```C++

#include "tp_fpga.h"

#include "wius_spi.h"

// Generic commands
#define SPI_READ_CFG 1
#define SPI_WRITE_CFG 2
#define SP_RD_FIFO 16
#define SPI_WR_FIFO 17

#define SPI_DUMMY_ADDR 0

// Commands for User logic (System controller)
#define SYS_CTRL_CMD_DUMMY 0
#define SYS_CTRL_CMD_START 1
#define SYS_CTRL_CMD_RESET 2
#define SYS_CTRL_CMD_RD_EN 3
#define SYS_CTRL_CMD_ECHO 4

// Commands for Memory Controller
#define MEM_CTRL_WR_CMD 1
#define MEM_CTRL_RD_CMD 0

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

    LOG_RET_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, len, wait));

    return status;
}

sl_status_t tp_fpga_write_reg(uint32_t reg_value, uint8_t reg_addr)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[8];

    tx_buf[0] = SPI_WR_FIFO;
    tx_buf[1] = SPI_DUMMY_ADDR;
    tx_buf[2] = MEM_CTRL_WR_CMD;
    tx_buf[3] = reg_addr;
    memcpy(tx_buf + 4, &reg_value, 4);

    LOG_RET_STATUS(wius_spi_send(WIUS_SPI_INST_0, tx_buf, 8, true));

    return status;
}

sl_status_t tp_fpga_send_read_reg_cmd(uint8_t reg_addr)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[8];

    tx_buf[0] = SPI_WR_FIFO;
    tx_buf[1] = SPI_DUMMY_ADDR;
    tx_buf[2] = MEM_CTRL_RD_CMD;
    tx_buf[3] = reg_addr;
    memset(tx_buf + 4, 0, 4);

    LOG_RET_STATUS(wius_spi_send(WIUS_SPI_INST_0, tx_buf, 8, true));

    return status;
}

sl_status_t tp_fpga_write_reg_safe(uint32_t reg_value, uint8_t reg_addr)
{
    sl_status_t status = SL_STATUS_OK;
    static uint8_t tx_buf[8 + 2];
    static uint8_t rx_buf[8 + 2];

    LOG_RET_STATUS(tp_fpga_write_reg(reg_value, reg_addr));

    LOG_RET_STATUS(tp_fpga_write_reg(0, 0));

    LOG_RET_STATUS(tp_fpga_read_fifo(tx_buf, rx_buf, 8 + 2, true));

    LOG_RET_STATUS(tp_fpga_send_read_reg_cmd(reg_addr));

    LOG_RET_STATUS(tp_fpga_read_fifo(tx_buf, rx_buf, 8 + 2, true));

    uint32_t reg_value_result = *((uint32_t *)(rx_buf + 2));

    if (reg_value != reg_value_result)
    {
        if (!TP_TEST_MODE)
        {
            log_error("Expected 0x%08lX, got 0x%08lX", reg_value, reg_value_result);
            return SL_STATUS_FAIL;
        }
        else
        {
            log_warn("Expected 0x%08lX, got 0x%08lX", reg_value, reg_value_result);
        }
    }

    return status;
}

sl_status_t tp_fpga_write_cfg(uint8_t value)
{
    sl_status_t status = SL_STATUS_OK;
    static uint8_t tx_buf[2];

    tx_buf[0] = SPI_WRITE_CFG;
    tx_buf[1] = value;

    status = wius_spi_send(WIUS_SPI_INST_0, tx_buf, 2, true);
    if (SL_STATUS_OK != status)
    {
        log_error("SPI CFG write failed!");
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

    LOG_RET_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

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

    LOG_RET_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    *answer = rx_buf[2];

    return status;
}

sl_status_t tp_fpga_init(void)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t answer = 0;

    LOG_RET_STATUS(tp_fpga_write_cfg(6));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    LOG_RET_STATUS(tp_fpga_read_cfg(&answer));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    if ((answer & 0b111) != 6)
    {
        log_warn("CFG reg expected 6, got %u", (answer & 0b111));
        return SL_STATUS_BUS_ERROR;
    }

    for (uint8_t i = 0; i < TP_NUM_DEFAULT_REGS; i++)
    {
        LOG_RET_STATUS(tp_fpga_write_reg_safe(default_values[i], default_registers[i]));
        delay_ns(TP_FPGA_SPI_DELAY_NS);
        // delay_ms(10);
    }

    return status;
}

sl_status_t tp_fpga_trigger_shot(void)
{
    sl_status_t status = SL_STATUS_OK;

    LOG_RET_STATUS(tp_fpga_write_reg(SYS_CTRL_CMD_RESET, 0));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    LOG_RET_STATUS(tp_fpga_write_reg(SYS_CTRL_CMD_START, 0));
    delay_ns(TP_FPGA_SPI_DELAY_NS);
    delay_ms(3);
    LOG_RET_STATUS(tp_fpga_write_reg(SYS_CTRL_CMD_RD_EN, 0));
    delay_ns(2400);

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

sl_status_t tp_fpga_empty_tx(void)
{
    uint8_t tx_buf[8 + 2] = {0};
    uint8_t rx_buf[8 + 2] = {0};

    return tp_fpga_read_fifo(tx_buf, rx_buf, 8 + 2, true);
}

sl_status_t tp_fpga_en_read(void)
{
    return tp_fpga_write_reg(SYS_CTRL_CMD_RD_EN, 0);
}
```


