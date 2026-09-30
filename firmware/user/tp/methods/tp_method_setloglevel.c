/**
 * @file tp_method_setloglevel.c
 *
 * @brief TinyProbe set log level method implementation file
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

#include "tp_method_setloglevel.h"

methods_status tp_method_setloglevel(const methods_setloglevel_args *req, void *userdata)
{
    UNUSED(req);
    UNUSED(userdata);

    // log_set_level((log_Level)req->level);
    // log_info("Log level set to %s", bitlog_level_strings[(log_Level)req->level]);
    log_warn("Not implemented");

    return methods_status_OK;
}
