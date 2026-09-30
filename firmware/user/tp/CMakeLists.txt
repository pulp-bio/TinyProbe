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

add_subdirectory(common)
add_subdirectory(hal)
add_subdirectory(methods)

add_library(user_tp STATIC
	tp.c
	tp_methods.c
)
user_configure_target(user_tp)
target_link_libraries(user_tp PUBLIC
	user_common
	wius
	tp_common
	tp_hal
	tp_methods
)

nanopb_generate_cpp(TARGET proto "${NANOPB_PROTO_DIR}/codegen/methods.proto")
target_link_libraries(proto user_options)
target_link_libraries(nanopb user_options)
target_link_libraries(tp_methods PUBLIC
	proto
)
