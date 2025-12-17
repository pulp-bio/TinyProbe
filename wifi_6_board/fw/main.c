/**
 * @file main.c
 *
 * @brief User main source file
 *
 * @date 17.12.2025
 * @copyright ETH Zurich. All rights reserved.
 *
 * @author Cédric Hirschi, ETH Zürich
 *
 * @ingroup common
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

#include "sl_main_init.h"
#include "sl_main_kernel.h"

#include "SEGGER_RTT.h"

#include "user/user.h"

int main(void)
{
  // Initialize Silicon Labs device, system, service(s) and protocol stack(s).
  sl_main_second_stage_init();

  user_init();
}
