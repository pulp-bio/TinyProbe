/**
 * @file tp_tx.c
 *
 * @brief TX chip driver for TinyProbe source file
 *
 * @date 08.09.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
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

#include "tp_tx.h"

#include "wius_spi.h"

// TX chip receives packages of 42 bits.
// We can send 48 bits package (6 bytes)
#define XFER_PACK_LEN 6

// For pattern generator
#define LVL_PHV 0b010
#define LVL_ZERO 0b011
#define LVL_MHV 0b001
#define LVL_TERMINATE 0b111

// Commands
#define CMD_READEN_0 (0)
#define CMD_READEN_1 (1 << 1)
#define CMD_READEN_2 (1 << 2)

sl_status_t tp_tx_write_reg(uint16_t address, uint32_t value)
{
    sl_status_t status = SL_STATUS_OK;
    uint64_t tx_data = 0;
    uint8_t tx_buf[XFER_PACK_LEN];
    uint8_t rx_buf[XFER_PACK_LEN];

    tx_data = address;
    tx_data = (tx_data << 32) | value;
    tx_data <<= 6;

    for (int i = XFER_PACK_LEN; i > 0; i--)
    {
        tx_buf[XFER_PACK_LEN - i] = (tx_data >> 8 * (i - 1)) & 0xFF;
    }

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, XFER_PACK_LEN, true));

    return status;
}

sl_status_t tp_tx_read_reg(uint16_t address, uint32_t *value)
{
    sl_status_t status = SL_STATUS_OK;
    uint64_t tx_data = 0;
    uint8_t tx_buf[XFER_PACK_LEN];
    uint8_t rx_buf[XFER_PACK_LEN];

    tx_data = address;
    tx_data = (tx_data << 32);
    tx_data <<= 6;

    CHECK_STATUS(tp_tx_write_reg(0, CMD_READEN_1));
    delay_ns(TP_AFE_SPI_DELAY_NS);

    for (int i = XFER_PACK_LEN; i > 0; i--)
    {
        tx_buf[XFER_PACK_LEN - i] = (tx_data >> 8 * (i - 1)) & 0xFF;
    }

    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, XFER_PACK_LEN, true));

    uint64_t reg_value_1 = (uint64_t)(rx_buf[1] & 0b111111) << 32;
    for (int i = 4; i > 0; i--)
    {
        reg_value_1 |= rx_buf[XFER_PACK_LEN - i] << 8 * (i - 1);
    }

    CHECK_STATUS(tp_tx_write_reg(0, CMD_READEN_2));
    delay_ns(TP_AFE_SPI_DELAY_NS);
    CHECK_STATUS(wius_spi_xfer(WIUS_SPI_INST_0, tx_buf, rx_buf, XFER_PACK_LEN, true));

    uint64_t reg_value_2 = (uint64_t)(rx_buf[1] & 0b111111) << 32;
    for (int i = 4; i > 0; i--)
    {
        reg_value_2 |= rx_buf[XFER_PACK_LEN - i] << 8 * (i - 1);
    }

    delay_ns(TP_AFE_SPI_DELAY_NS);
    CHECK_STATUS(tp_tx_write_reg(0, CMD_READEN_0));

    reg_value_1 >>= 6;
    reg_value_2 >>= 6;

    *value = (uint32_t)(reg_value_1 | reg_value_2);

    return status;
}

sl_status_t tp_tx_write_reg_safe(uint16_t address, uint32_t value)
{
    sl_status_t status = SL_STATUS_OK;
    uint32_t read_value = 0;

    CHECK_STATUS(tp_tx_write_reg(address, value));
    CHECK_STATUS(tp_tx_read_reg(address, &read_value));

    if (read_value != value)
    {
        LOG_W("Expected 0x%08lX, got 0x%08lX at 0x%02x", value, read_value, address);
        //        status = SL_STATUS_FAIL;
    }
    else
    {
        LOG_D("0x%08lX at 0x%02x OK", value, address);
    }

    return status;
}

sl_status_t tp_tx_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    // Datasheet p 103
    // Set delays for all the channels to 0
    for (uint32_t reg_addr = 0x20; reg_addr < (0x2F + 1); reg_addr++)
    {
        CHECK_STATUS(tp_tx_write_reg_safe(reg_addr, 0));
    }
    // Write pattern profile
    CHECK_STATUS(tp_tx_write_reg_safe(0x120, 0x78));
    // Set TX_BF_MODE = 1
    CHECK_STATUS(tp_tx_write_reg_safe(0x18, 1));

    // Wait at least 200 TX BF
    delay_ns(40000);

    //// SOFTWARE RESET ////
    CHECK_STATUS(tp_tx_write_reg_safe(0x00, 1));

    //    //// JUST for testing : Enable/Disable Power down for pulsers ////
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x1B, 0xffffffff);
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x1B, 0);

    //// DYNAMIC POWER MODE ////
    // EN_DYN_LDO = 1
    CHECK_STATUS(tp_tx_write_reg_safe(0x19, 1 << 30));

    delay_ns(40000);
    // DIS_DYN_CNTRL_1 = 0
    CHECK_STATUS(tp_tx_write_reg_safe(0x0F, 0));
    // DIS_DYN_CTRL_2 = 0
    CHECK_STATUS(tp_tx_write_reg_safe(0x06, 0));

    //    // DIS_DYN_CNTRL_1 = 1
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x0F, (1<<4));
    //    // DIS_DYN_CTRL_2 = 1
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x06, (1<<4));

    // Put low max current
    // DRV strength is controlled by reg, 0.6 A
    CHECK_STATUS(tp_tx_write_reg_safe(0x17, (6 << 2)));

    //// Programm pattern profile ////

    // BF clock 100 mHz, output pulse freq - 8.2 MHz
    // // Configure pattern profile 1
    uint32_t pat_reg = 0;
    // LVL_1 = 0, PER_1 = 0
    pat_reg = (LVL_ZERO << 0) | (0 << 3);
    // LVL_2 = + HV , PER_2 = 4
    pat_reg |= (LVL_PHV << 8) | (4 << 11);
    // LVL_3 = - HV , PER_3 = 4
    pat_reg |= (LVL_MHV << 16) | (4 << 19);
    // LVL_4 = + HV , PER_4 = 4
    pat_reg |= (LVL_PHV << 24) | (4 << 27);
    CHECK_STATUS(tp_tx_write_reg_safe(0x120, pat_reg));
    CHECK_STATUS(tp_tx_write_reg_safe(0x124, pat_reg));

    pat_reg = 0;
    // LVL_5 = - HV, PER_5 = 4
    pat_reg = (LVL_MHV << 0) | (4 << 3);
    // LVL_6 = 0 , PER_6 = 4
    pat_reg |= (LVL_ZERO << 8) | (4 << 11);
    // LVL_7 = - HV , PER_7 = 0
    pat_reg |= (LVL_TERMINATE << 16) | (0 << 19);
    CHECK_STATUS(tp_tx_write_reg_safe(0x121, pat_reg));
    CHECK_STATUS(tp_tx_write_reg_safe(0x125, pat_reg));

    //    // BF clock 100 mHz, output pulse freq - 5.0 MHz
    //    // Configure pattern profile 1
    //    uint32_t pat_reg = 0;
    //    // LVL_1 = 0, PER_1 = 0
    //    pat_reg = (LVL_ZERO << 0) | (0 << 3);
    //    // LVL_2 = + HV , PER_2 = 8
    //    pat_reg |= (LVL_PHV << 8) | (8 << 11);
    //    // LVL_3 = - HV , PER_3 = 8
    //    pat_reg |= (LVL_MHV << 16) | (8 << 19);
    //    // LVL_4 = + HV , PER_4 = 8
    //    pat_reg |= (LVL_PHV << 24) | (8 << 27);
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x120, pat_reg);
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x124, pat_reg);
    //
    //    pat_reg = 0;
    //    // LVL_5 = - HV, PER_5 = 8
    //    pat_reg = (LVL_MHV << 0) | (8 << 3);
    //    // LVL_6 = 0 , PER_6 = 8
    //    pat_reg |= (LVL_ZERO << 8) | (8 << 11);
    //    // LVL_7 = TERMINATE , PER_7 = 0
    //    pat_reg |= (LVL_TERMINATE << 16) | (0 << 19);
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x121, pat_reg);
    //    CHECK_STATUS(tp_tx_write_reg_safe(0x125, pat_reg);

    // Select pattern profile 1 for channel group 1 and 2, ie
    // Set PAT_SEL_G1 = 1
    CHECK_STATUS(tp_tx_write_reg_safe(0x1F, 1));
    // PAT_SEL_G2 = 1
    CHECK_STATUS(tp_tx_write_reg_safe(0x1E, 1));

    // Set LOAD_PROF to 1
    CHECK_STATUS(tp_tx_write_reg_safe(0x00, (1 << 2)));

    //// SET TURN ON DELAYS (4 * reg_val + 5 + 2) ////
    // TR_SW_DEL_G2 and TR_SW_DEL_G4
    CHECK_STATUS(tp_tx_write_reg_safe(0x15, (70 << 16) | (70)));
    // TR_SW_DEL_G1 and TR_SW_DEL_G3
    CHECK_STATUS(tp_tx_write_reg_safe(0x16, (70 << 16) | (70)));

    //// ENABLE TX BF MODE ////
    // Set TX_BF_MODE = 1,
    // write TX_START_DELAY [26:18] to get a minimum delay of 2 us,
    // write TR_SW_DEL_MODE to enable TR switch at the end of pattern
    // Delays for Turn on are relative to the end of pattern
    CHECK_STATUS(tp_tx_write_reg_safe(0x18, 0x008C0003));

    return status;
}