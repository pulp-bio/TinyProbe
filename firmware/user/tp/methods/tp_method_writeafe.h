/**
 * @file tp_method_writeafe.h
 *
 * @brief TinyProbe AFE write method header file
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

#pragma once

#include "common.h"
#include "methods.pb.h"

/**
 * @brief JSON-RPC method handler for the "writeafe" method
 *
 * @param args Command arguments struct
 * @param userdata User data pointer
 *
 * @return OK if method executed successfully, otherwise an error code
 *
 */
methods_status tp_method_writeafe(const methods_writeafe_args *args, void *userdata);
