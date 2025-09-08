#[[
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
]]

add_library(tinyprobe STATIC
    tp_afe.o
    tp_buffer.c
    tp_command.c
    tp_fpga.c
    tp_mux.c
    tp_power.c
    tp_tx.c
    tp.c
)
target_include_directories(tinyprobe PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(tinyprobe PUBLIC
    slc_wius_fw
    common
)