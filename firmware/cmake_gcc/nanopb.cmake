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

set(NANOPB_ROOT_DIR "${CMAKE_CURRENT_LIST_DIR}/../vendor/nanopb")
set(CMAKE_MODULE_PATH "${NANOPB_ROOT_DIR}/extra")
set(NANOPB_SRC_ROOT_FOLDER "${NANOPB_ROOT_DIR}")

if(CMAKE_HOST_UNIX)
	set(NANOPB_PREPARED_GENERATOR_DIR "${CMAKE_BINARY_DIR}/nanopb-generator")
	execute_process(
		COMMAND ${CMAKE_COMMAND}
			-DNANOPB_GENERATOR_SOURCE_DIR=${NANOPB_ROOT_DIR}/generator
			-DNANOPB_GENERATOR_DEST_DIR=${NANOPB_PREPARED_GENERATOR_DIR}
			-P ${CMAKE_CURRENT_LIST_DIR}/PrepareNanopbGenerator.cmake
		COMMAND_ERROR_IS_FATAL ANY
	)
	find_program(PROTOBUF_PROTOC_EXECUTABLE NAMES protoc REQUIRED)
	set(NANOPB_GENERATOR_SOURCE_DIR "${NANOPB_PREPARED_GENERATOR_DIR}" CACHE PATH "Prepared nanopb generator source" FORCE)
endif()

find_package(Nanopb REQUIRED)

set(NANOPB_PROTO_DIR "${CMAKE_CURRENT_LIST_DIR}/../../config")
