/**
 * @file tp.h
 *
 * @brief TinyProbe main header file
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
 * @brief Initialize the FPGA (SPI, GPIOs, register values)
 *
 * @retval SL_STATUS_OK: Success
 * @retval other: SPI, GPIO interrupt or register initialization failed
 *
 */
sl_status_t tp_init(void);
void tp_main_thread(void);

sl_status_t tp_ping(uint8_t *args, uint16_t args_length);
sl_status_t tp_en_replies(uint8_t *args, uint16_t args_length);
sl_status_t tp_sw_mux(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_spi(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_fpga(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_afe(uint8_t *args, uint16_t args_length);
sl_status_t tp_write_tx(uint8_t *args, uint16_t args_length);
sl_status_t tp_delay_ns(uint8_t *args, uint16_t args_length);
sl_status_t tp_sleep_ms(uint8_t *args, uint16_t args_length);
sl_status_t tp_ctrl_pwr(uint8_t *args, uint16_t args_length);
sl_status_t tp_trigger_shot(uint8_t *args, uint16_t args_length);