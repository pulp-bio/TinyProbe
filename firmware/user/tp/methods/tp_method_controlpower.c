/**
 * @file tp_method_controlpower.c
 *
 * @brief TinyProbe control power method implementation file
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

#include "tp_method_controlpower.h"

#include "tp_power.h"

methods_status tp_method_controlpower(const methods_controlpower_args *args, void *userdata)
{
    UNUSED(userdata);

    tp_power_set((tp_power_domain_t)args->domain, args->enable);

    return methods_status_OK;
}
