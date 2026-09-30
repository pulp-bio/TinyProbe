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

#!/usr/bin/env bash
set -euo pipefail

extension_path="$(slt where simplicity-sdk)/extension/wiseconnect3"
wiseconnect_path="$(slt where wiseconnect)"

# Create extension directory
/bin/bash -lc "mkdir -p ${extension_path}"

# Symlink WiseConnect SDK files
/bin/bash -lc "cp -a ${wiseconnect_path}/* ${extension_path}/"

# Trust the extension
/bin/bash -lc "slc signature trust -extpath ${extension_path}"
