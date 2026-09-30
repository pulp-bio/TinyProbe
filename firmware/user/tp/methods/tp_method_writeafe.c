/**
 * @file tp_method_writeafe.c
 *
 * @brief TinyProbe AFE write method implementation file
 *
 * @date 03.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 * @author Sergei Vostrikov, ETH Zürich
 *
 * @ingroup tinyprobe_methods
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

#include "tp_method_writeafe.h"

#include "tp_afe.h"

methods_status tp_method_writeafe(const methods_writeafe_args *args, void *userdata)
{
    UNUSED(userdata);

    sl_status_t status = SL_STATUS_OK;

    // log_debug("Writing %lu to %u (dtgc=%d)", args->value, args->address, args->dtgc);

    if (args->dtgc)
    {
        status = tp_afe_write_reg_dtgc(args->address, args->value);
    }
    else
    {
        status = tp_afe_write_reg(args->address, args->value);
    }
    if (SL_STATUS_OK != status)
    {
        LOG_STATUS(status);
        return methods_status_UNKNOWN_ERROR;
    }

    return methods_status_OK;
}
