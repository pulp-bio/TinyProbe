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

cmake_policy(SET CMP0053 NEW)

if(NOT DEFINED NANOPB_GENERATOR_SOURCE_DIR)
  message(FATAL_ERROR "NANOPB_GENERATOR_SOURCE_DIR is required")
endif()

if(NOT DEFINED NANOPB_GENERATOR_DEST_DIR)
  message(FATAL_ERROR "NANOPB_GENERATOR_DEST_DIR is required")
endif()

file(REMOVE_RECURSE "${NANOPB_GENERATOR_DEST_DIR}")
file(MAKE_DIRECTORY "${NANOPB_GENERATOR_DEST_DIR}")
file(COPY "${NANOPB_GENERATOR_SOURCE_DIR}/" DESTINATION "${NANOPB_GENERATOR_DEST_DIR}")

file(GLOB_RECURSE NANOPB_GENERATOR_FILES "${NANOPB_GENERATOR_DEST_DIR}/*")

foreach(NANOPB_GENERATOR_FILE IN LISTS NANOPB_GENERATOR_FILES)
  if(IS_DIRECTORY "${NANOPB_GENERATOR_FILE}")
    continue()
  endif()

  get_filename_component(NANOPB_GENERATOR_NAME "${NANOPB_GENERATOR_FILE}" NAME)
  if(NANOPB_GENERATOR_NAME MATCHES "\\.bat$")
    continue()
  endif()

  file(READ "${NANOPB_GENERATOR_FILE}" NANOPB_GENERATOR_CONTENT)
  string(REPLACE "\r\n" "\n" NANOPB_GENERATOR_CONTENT "${NANOPB_GENERATOR_CONTENT}")
  string(REPLACE "\r" "\n" NANOPB_GENERATOR_CONTENT "${NANOPB_GENERATOR_CONTENT}")
  file(WRITE "${NANOPB_GENERATOR_FILE}" "${NANOPB_GENERATOR_CONTENT}")
endforeach()
