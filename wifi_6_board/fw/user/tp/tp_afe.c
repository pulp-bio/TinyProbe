/**
 * @file tp_afe.c
 *
 * @brief AFE driver for TinyProbe source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup tinyprobe
 *
 */

#include "tp_afe.h"

#include "wius_spi.h"

// Define for Globas register 0
#define DTGC_WR_EN 0x10
#define REG_READ_EN 0x02
#define AFE_SOFT_RST 0x01

#define ADC_REG_41_PLLRST1 0x4000
#define ADC_REG_42_PLLRST2 0x4000

typedef struct _tp_afe_reg
{
    uint8_t addr;
    uint16_t data;
} _tp_afe_reg_t;

#define NUM_OF_ADC_VCA_REGS (55 + 23)

_tp_afe_reg_t const tp_afe_adc_vca_reg_init_seq[NUM_OF_ADC_VCA_REGS] =
    {
        // Global Register
        {0x00, 0x0000},
        // Standart LVDs rate, LVDS enabled,
        // No global PDN
        {0x01, 0x0000},
        // No tests patterns
        {0x02, 0x0000},
        // SER_DATA_RATE = 10x
        // Digital gain disabled, no offset, ser. factor = 10x
        {0x03, 0x6008},
        // 10 bit resolution, MSB first, twos complementary
        {0x04, 0x0003},
        // Default
        {0x05, 0x0000},
        // Default
        {0x07, 0x0000},
        // Default
        {0x08, 0x0000},
        // ADC LOW power mode
        {0x0B, 0x0800},
        // Default params of digital gain and offset
        // for ADC(1-4)o and ADC(1-4)e
        {0x0D, 0x0000},
        {0x0E, 0x0000},
        {0x0F, 0x0000},
        {0x10, 0x0000},
        {0x11, 0x0000},
        {0x12, 0x0000},
        {0x13, 0x0000},
        {0x14, 0x0000},
        // Disabled Test patterns on LVDS
        {0x15, 0x0000},
        {0x17, 0x0000},
        // LVDS 1-4 pdn is disabled
        {0x18, 0x0000},
        // Default params of digital gain and offset
        // for ADC(5-8)o and ADC(5-8)e
        {0x19, 0x0000},
        {0x1A, 0x0000},
        {0x1B, 0x0000},
        {0x1C, 0x0000},
        {0x1D, 0x0000},
        {0x1E, 0x0000},
        {0x1F, 0x0000},
        {0x20, 0x0000},
        // Disabled Test patterns on LVDS
        {0x21, 0x0000},
        {0x23, 0x0000},
        // LVDS 5-8 pdn is disabled
        {0x24, 0x0000},
        // Default params of digital gain and offset
        // for ADC(9-12)o and ADC(9-12)e
        {0x25, 0x0000},
        {0x26, 0x0000},
        {0x27, 0x0000},
        {0x28, 0x0000},
        {0x29, 0x0000},
        {0x2A, 0x0000},
        {0x2B, 0x0000},
        {0x2C, 0x0000},
        // Disabled Test patterns on LVDS
        {0x2D, 0x0000},
        {0x2F, 0x0000},
        // LVDS 9-12 pdn is disabled
        {0x30, 0x0000},
        // Default params of digital gain and offset
        // for ADC(13-16)o and ADC(13-16)e
        {0x31, 0x0000},
        {0x32, 0x0000},
        {0x33, 0x0000},
        {0x34, 0x0000},
        {0x35, 0x0000},
        {0x36, 0x0000},
        {0x37, 0x0000},
        {0x38, 0x0000},
        // Disabled Test patterns on LVDS
        {0x39, 0x0000},
        {0x3B, 0x0000},
        // LVDS 13-16 pdn is disabled
        {0x3C, 0x0000},

        // PLLRST 1 is not active
        {0x41, 0x0000},
        // PLLRST 2 is not active
        {0x42, 0x0000},
        // LVDS_DCLK_DELAY_PROG is default
        {0x43, 0x0000},

        // VCA registers
        // Default
        {0xC0, 0x0000},
        {0xC1, 0x0000},
        {0xC2, 0x0000},
        {0xC3, 0x0000},
        {0xC4, 0x0000},
        // Default Power down settings for individual ch
        {0xC5, 0x0000},
        // Default Power down settings for all ch
        {0xC6, 0x0000},
        // PGA_gain 27 dB, LNA gain 21 dB
        {0xC7, 0x0005},
        // Low power VCA mode
        {0xC8, 0x0001},
        // Default
        {0xCA, 0x0000},
        {0xCB, 0x0000},
        {0xCC, 0x0000},
        {0xCD, 0x0000},
        // Power down ch 17-32
        {0xCE, 0x0000},
        {0xD0, 0x0000},
        {0xD1, 0x0007},
        {0xD4, 0x0001},
        // Temp sensor disabled
        {0xE0, 0x0000},
        // Default TGC profile settings
        {0xF9, 0x0000},
        {0xFA, 0x0000},
        {0xFB, 0x0000},
        {0xFC, 0x0000},
        // {0xFD, 0x0000},
};

#define NUM_OF_DTGC_REGS (23)

_tp_afe_reg_t const tp_afe_dtgc_reg_init_seq[NUM_OF_DTGC_REGS] =
    {
        // Default start/stop gain for profile 0
        {0xA1, 0x0000},
        // Default pos/neg step for profile 0
        {0xA2, 0x0000},
        // Default start/stop index for profile 0
        {0xA3, 0x0000},
        // Default start gain time for profile 0
        {0xA4, 0x0000},
        // Default start gain time for profile 0
        {0xA5, 0x0000},
        // Default start/stop gain for profile 1
        {0xA6, 0x0000},
        // Default pos/neg step for profile 1
        {0xA7, 0x0000},
        // Default start/stop index for profile 1
        {0xA8, 0x0000},
        // Dfault start gain time for profile 1
        {0xA9, 0x0000},
        // Default start gain time for profile 1
        {0xAA, 0x0000},
        // Default start/stop gain for profile 2
        {0xAB, 0x0000},
        // Default pos/neg step for profile 2
        {0xAC, 0x0000},
        // Default start/stop index for profile 2
        {0xAD, 0x0000},
        // Default start gain time for profile 2
        {0xAE, 0x0000},
        // Default start gain time for profile 2
        {0xAF, 0x0000},
        // Default start/stop gain for profile 3
        {0xB0, 0x0000},
        // Default pos/neg step for profile 3
        {0xB1, 0x0000},
        // Default start/stop index for profile 3
        {0xB2, 0x0000},
        // Dfault start gain time for profile 3
        {0xB3, 0x0000},
        // Default start gain time for profile 3
        {0xB4, 0x0000},
        //  Manual gain TGC is default
        {0xB5, 0x0000},
        // mode Programmable fixed gain
        {0xB6, 0x8000},
        // Default
        {0xB7, 0x8000}};

sl_status_t tp_afe_write_reg(uint8_t address, uint16_t value)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[3] = {address, (value >> 8) & 0xFF, value & 0xFF};
    uint8_t rx_buf[3];

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    delay_ns(TP_AFE_SPI_DELAY_NS);

    return status;
}

sl_status_t tp_afe_read_reg(uint8_t address, uint16_t *value)
{
    sl_status_t status = SL_STATUS_OK;

    CHECK_STATUS(tp_afe_write_reg(0, REG_READ_EN));

    uint8_t tx_buf[3] = {address, 0, 0};
    uint8_t rx_buf[3];

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    delay_ns(TP_AFE_SPI_DELAY_NS);

    CHECK_STATUS(tp_afe_write_reg(0, 0));

    *value = (uint16_t)((rx_buf[1] << 8) | rx_buf[2]);

    return status;
}

sl_status_t tp_afe_write_reg_safe(uint8_t address, uint16_t value)
{
    sl_status_t status = SL_STATUS_OK;
    uint16_t read_value = 0;

    CHECK_STATUS(tp_afe_write_reg(address, value));
    CHECK_STATUS(tp_afe_read_reg(address, &read_value));

    if (read_value != value)
    {
        LOG_W("Expected 0x%04X, got 0x%04X at 0x%02X", value, read_value, address);
        //        status = SL_STATUS_FAIL;
    }
    else
    {
        LOG_D("0x%04X at 0x%02X OK", value, address);
    }

    return status;
}

sl_status_t tp_afe_write_reg_dtgc(uint8_t address, uint16_t value)
{
    sl_status_t status = SL_STATUS_OK;
    uint8_t tx_buf[3] = {address, (value >> 8) & 0xFF, value & 0xFF};
    uint8_t rx_buf[3] = {0};

    // Write bit DTGC_WR_EN to Global reg 0 (all the others are 0)
    CHECK_STATUS(tp_afe_write_reg(0, DTGC_WR_EN));
    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    delay_ns(TP_AFE_SPI_DELAY_NS);

    // Clear bit DTGC_WR_EN in Global reg 0 (all the others are 0)
    CHECK_STATUS(tp_afe_write_reg(0, 0));

    return status;
}

sl_status_t tp_afe_read_reg_dtgc(uint8_t address, uint16_t *value)
{
    sl_status_t status = SL_STATUS_OK;

    CHECK_STATUS(tp_afe_write_reg(0, REG_READ_EN | DTGC_WR_EN));

    uint8_t tx_buf[3] = {address, 0, 0};
    uint8_t rx_buf[3] = {0};

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, 3, true));

    delay_ns(TP_AFE_SPI_DELAY_NS);

    CHECK_STATUS(tp_afe_write_reg(0, DTGC_WR_EN));

    *value = (uint16_t)((rx_buf[1] << 8) | rx_buf[2]);

    return status;
}

sl_status_t tp_afe_write_reg_dtgc_safe(uint8_t address, uint16_t value)
{
    sl_status_t status = SL_STATUS_OK;
    uint16_t read_value = 0;

    CHECK_STATUS(tp_afe_write_reg_dtgc(address, value));
    CHECK_STATUS(tp_afe_read_reg_dtgc(address, &read_value));

    if (read_value != value)
    {
        LOG_W("Expected 0x%04X, got 0x%04X at 0x%02x", value, read_value, address);
        //        status = SL_STATUS_FAIL;
    }
    else
    {
        LOG_D("0x%04X at 0x%02X OK", value, address);
    }

    return status;
}

sl_status_t tp_afe_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    // CHECK_STATUS(tp_afe_write_reg_safe(tp_afe_adc_vca_reg_init_seq[0].addr,
    //                                    tp_afe_adc_vca_reg_init_seq[0].data));

    for (uint32_t i = 0; i < NUM_OF_ADC_VCA_REGS; i++)
    {
        CHECK_STATUS(tp_afe_write_reg_safe(tp_afe_adc_vca_reg_init_seq[i].addr,
                                           tp_afe_adc_vca_reg_init_seq[i].data));
        // delay_ms(10);
    };

    // CHECK_STATUS(tp_afe_write_reg_safe(tp_afe_adc_vca_reg_init_seq[0].addr,
    //                                    tp_afe_adc_vca_reg_init_seq[0].data));

    for (uint32_t i = 0; i < NUM_OF_DTGC_REGS; i++)
    {
        CHECK_STATUS(tp_afe_write_reg_dtgc_safe(tp_afe_dtgc_reg_init_seq[i].addr,
                                                tp_afe_dtgc_reg_init_seq[i].data));
        // delay_ms(10);
    };

    // Write the PLLRST bits to 1
    CHECK_STATUS(tp_afe_write_reg(0x41, ADC_REG_41_PLLRST1));
    CHECK_STATUS(tp_afe_write_reg(0x42, ADC_REG_42_PLLRST2));

    delay_ns(100000);

    // Write the PLLRST bits to 0
    CHECK_STATUS(tp_afe_write_reg(0x41, ADC_REG_41_PLLRST1));
    CHECK_STATUS(tp_afe_write_reg(0x42, ADC_REG_42_PLLRST2));

    delay_ns(100000);

    return status;
}

sl_status_t tp_afe_test_pattern(tp_afe_patt_t pattern)
{
    sl_status_t status = SL_STATUS_OK;
    uint16_t temp = 0;

    CHECK_STATUS(tp_afe_read_reg(0x02, &temp));

    temp |= ((uint16_t)pattern << 7);

    CHECK_STATUS(tp_afe_write_reg_safe(0x02, temp));

    return status;
}
