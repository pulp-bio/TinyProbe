/**
 * @file wius_power.c
 *
 * @brief Power management for WiUS source file
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

#include "wius_power.h"

#include "sl_si91x_power_manager.h"

sl_status_t wius_power_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    // Initialize the SI91X power manager.
    status = sl_si91x_power_manager_init();
    if (status == SL_STATUS_ALREADY_INITIALIZED)
    {
        status = SL_STATUS_OK;
    }
    else if (status != SL_STATUS_OK)
    {
        return status;
    }

    // Set default power mode (low power) initially.
    CHECK_STATUS(sl_si91x_power_manager_add_ps_requirement(SL_SI91X_POWER_MANAGER_PS4));
    CHECK_STATUS(wius_power_set(WIUS_POWER_MODE_LOW));

    return status;
}

sl_status_t wius_power_set(wius_power_mode_t mode)
{
    sl_status_t status = SL_STATUS_OK;

    switch (mode)
    {
    case WIUS_POWER_MODE_LOW:
        // For LOW mode, remove the high performance (PS4) requirement and add the low-power (PS3) requirement.
        // The call to set_clock_scaling with SL_SI91X_POWER_MANAGER_POWERSAVE
        // will configure the MCU to run at 40MHz (PS3 mode), as per the SDK defaults.
        CHECK_STATUS(sl_si91x_power_manager_remove_ps_requirement(SL_SI91X_POWER_MANAGER_PS4));
        CHECK_STATUS(sl_si91x_power_manager_add_ps_requirement(SL_SI91X_POWER_MANAGER_PS3));
        CHECK_STATUS(sl_si91x_power_manager_set_clock_scaling(SL_SI91X_POWER_MANAGER_POWERSAVE));
        break;

    case WIUS_POWER_MODE_HIGH:
        // For HIGH mode, remove the low-power (PS3) requirement and add the high-performance (PS4) requirement.
        // The clock scaling is set to SL_SI91X_POWER_MANAGER_PERFORMANCE to run at 180MHz.
        CHECK_STATUS(sl_si91x_power_manager_remove_ps_requirement(SL_SI91X_POWER_MANAGER_PS3));
        CHECK_STATUS(sl_si91x_power_manager_add_ps_requirement(SL_SI91X_POWER_MANAGER_PS4));
        CHECK_STATUS(sl_si91x_power_manager_set_clock_scaling(SL_SI91X_POWER_MANAGER_PERFORMANCE));
        break;

    default:
        return SL_STATUS_INVALID_PARAMETER;
    }

    // Update system ticks if needed after a clock change.
    common_tick_update();

    return status;
}
