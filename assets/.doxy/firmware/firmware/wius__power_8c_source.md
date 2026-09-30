

# File wius\_power.c

[**File List**](files.md) **>** [**firmware**](dir_d9edf6c004b4a7ff14fe9ae7a92214ee.md) **>** [**user**](dir_83392af1a298c3d0e842ea40b1e13d83.md) **>** [**wius**](dir_428ea0099726046bf3ca5149c3e3a453.md) **>** [**hal**](dir_7f08c57397c8971977b54cfee07615c0.md) **>** [**wius\_power.c**](wius__power_8c.md)

[Go to the documentation of this file](wius__power_8c.md)


```C++

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
    LOG_RET_STATUS(sl_si91x_power_manager_add_ps_requirement(SL_SI91X_POWER_MANAGER_PS4));
    LOG_RET_STATUS(wius_power_set(WIUS_POWER_MODE_LOW));

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
        LOG_RET_STATUS(sl_si91x_power_manager_remove_ps_requirement(SL_SI91X_POWER_MANAGER_PS4));
        LOG_RET_STATUS(sl_si91x_power_manager_add_ps_requirement(SL_SI91X_POWER_MANAGER_PS3));
        LOG_RET_STATUS(sl_si91x_power_manager_set_clock_scaling(SL_SI91X_POWER_MANAGER_POWERSAVE));
        break;

    case WIUS_POWER_MODE_HIGH:
        // For HIGH mode, remove the low-power (PS3) requirement and add the high-performance (PS4) requirement.
        // The clock scaling is set to SL_SI91X_POWER_MANAGER_PERFORMANCE to run at 180MHz.
        LOG_RET_STATUS(sl_si91x_power_manager_remove_ps_requirement(SL_SI91X_POWER_MANAGER_PS3));
        LOG_RET_STATUS(sl_si91x_power_manager_add_ps_requirement(SL_SI91X_POWER_MANAGER_PS4));
        LOG_RET_STATUS(sl_si91x_power_manager_set_clock_scaling(SL_SI91X_POWER_MANAGER_PERFORMANCE));
        break;

    default:
        return SL_STATUS_INVALID_PARAMETER;
    }

    // Update system ticks if needed after a clock change.
    common_tick_update();

    return status;
}
```


