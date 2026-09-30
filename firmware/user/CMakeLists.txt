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

set(USER_DIR ${CMAKE_CURRENT_SOURCE_DIR})
set(USER_VENDOR_DIR ${USER_DIR}/../vendor)
set(USER_VENDOR_LOG_DIR ${USER_VENDOR_DIR}/log)

add_library(user_options INTERFACE)
target_link_libraries(user_options INTERFACE
	slc
)
target_include_directories(user_options INTERFACE
	${USER_DIR}
	${USER_DIR}/common
	${USER_DIR}/tp
	${USER_DIR}/tp/common
	${USER_DIR}/tp/hal
	${USER_DIR}/tp/methods
	${USER_DIR}/wius
	${USER_DIR}/wius/hal
	${USER_DIR}/wius/common/jsonrpc
	${USER_VENDOR_LOG_DIR}
)

function(user_configure_target target)
	target_link_libraries(${target} PUBLIC user_options)
endfunction()

function(add_conditional_c_source target base_path)
    # Resolve relative paths relative to the current source directory
    if(NOT IS_ABSOLUTE "${base_path}")
        set(base_path "${CMAKE_CURRENT_SOURCE_DIR}/${base_path}")
    endif()

    set(c_file "${base_path}.c")
    set(o_file "${base_path}.o")

    if(EXISTS "${c_file}")
        # Custom command to compile .c directly into .o in the source tree
        add_custom_command(
            OUTPUT "${o_file}"
            COMMAND "${CMAKE_C_COMPILER}"
                    "$<LIST:TRANSFORM,$<TARGET_PROPERTY:${target},INCLUDE_DIRECTORIES>,PREPEND,-I>"
                    "$<TARGET_PROPERTY:${target},COMPILE_OPTIONS>"
                    "$<LIST:TRANSFORM,$<TARGET_PROPERTY:${target},COMPILE_DEFINITIONS>,PREPEND,-D>"
                    -c "${c_file}" -o "${o_file}"
            DEPENDS "${c_file}"
            COMMENT "Building ${o_file} next to source"
            VERBATIM
            COMMAND_EXPAND_LISTS
        )

        # Mark as GENERATED so CMake accepts an in-source build artifact
        set_source_files_properties("${o_file}" PROPERTIES GENERATED TRUE)

        # Add .c as a tracked source and .o as the object artifact
        target_sources("${target}" PRIVATE "${c_file}" "${o_file}")

    elseif(EXISTS "${o_file}")
        # Only the pre-compiled .o exists
        target_sources("${target}" PRIVATE "${o_file}")

    else()
        message(FATAL_ERROR "Neither '${c_file}' nor '${o_file}' could be found.")
    endif()
endfunction()

add_subdirectory(wius)
add_subdirectory(common)
add_subdirectory(tp)

add_library(user STATIC
	user.c
)
user_configure_target(user)
target_link_libraries(user PUBLIC
	user_common
	user_tp
)
