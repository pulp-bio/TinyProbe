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

add_library(tp_methods STATIC
	tp_method_controlpower.c
	tp_method_controlspi.c
	tp_method_delayms.c
	tp_method_delayns.c
	tp_method_ping.c
	tp_method_setloglevel.c
	tp_method_triggershot.c
	tp_method_writeafe.c
	tp_method_writefpga.c
	tp_method_writetx.c
)
user_configure_target(tp_methods)
target_link_libraries(tp_methods PUBLIC
	user_common
	wius
	tp_common
	tp_hal
)
