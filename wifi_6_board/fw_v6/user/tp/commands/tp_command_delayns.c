/**
 * @file tp_command_delayns.c
 *
 * @brief TinyProbe delay in nanoseconds command implementation file
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

#include "tp_command_delayns.h"

sl_status_t tp_delay_ns(uint8_t *args, uint16_t args_length)
{
  LOG_D("Executing");

  (void)args_length;

  // FIXME: delay_higher crashes program
  uint32_t delay_lower = GET(args, uint32_t, 0);
  //    uint32_t delay_higher = GET(args, uint32_t, 4);
  //    uint64_t delay = delay_higher << 32 | delay_lower;
  delay_ns(delay_lower);

  LOG_D("Done");

  return SL_STATUS_OK;
}
