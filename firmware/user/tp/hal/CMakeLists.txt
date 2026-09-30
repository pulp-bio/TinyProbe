# Copyright (C) 2026 ETH Zurich. All rights reserved.
#
# Authors:
#     - Cedric Hirschi, ETH Zurich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

add_library(tp_hal STATIC
	tp_fpga.c
	tp_mux.c
	tp_power.c
)
add_conditional_c_source(tp_hal tp_afe)
add_conditional_c_source(tp_hal tp_tx)

user_configure_target(tp_hal)
target_link_libraries(tp_hal PUBLIC
	user_common
	wius_hal
)
