/***************************************************************************//**
 * @file sl_ssi_instances.h.jinja
 * @brief SSI Driver Instance
 *******************************************************************************
 * # License
 * <b>Copyright 2024 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * SPDX-License-Identifier: Zlib
 *
 * The licensor of this software is Silicon Laboratories Inc.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 ******************************************************************************/

#ifndef SL_SSI_INSTANCES_H
#define SL_SSI_INSTANCES_H

#ifdef __cplusplus
extern "C" {
#endif



#include "sl_si91x_ssi_primary_config.h"



sl_ssi_control_config_t ssi_primary_configuration = {
    .bit_width = SL_SSI_PRIMARY_BIT_WIDTH,
    .device_mode = SL_SSI_PRIMARY_DEVICE_MODE,
    .clock_mode = SL_SSI_PRIMARY_CLOCK_MODE,
    .receive_sample_delay = SL_SSI_PRIMARY_RECEIVE_SAMPLE_DELAY,
    .baud_rate = SL_SSI_PRIMARY_BAUD,
    .transfer_mode = SL_SSI_PRIMARY_TRANSFER_MODE,
};


#ifdef __cplusplus
}
#endif

#endif // SL_SSI_INSTANCES_H
