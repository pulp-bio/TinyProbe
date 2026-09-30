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

cmake_path="$(slt where cmake)"
commander_path="$(slt where commander)"
gcc_arm_path="$(slt where gcc-arm-none-eabi)"
java_path="$(slt where java21)"
ninja_path="$(slt where ninja)"
slc_cli_path="$(slt where slc_cli_base)"

# Put in /etc/profile.d to have it available in login shells
cat <<EOF > /etc/profile.d/slt.sh
export PATH="${cmake_path}/bin:${commander_path}:${gcc_arm_path}/bin:${java_path}/jre/bin:${ninja_path}:${slc_cli_path}:\$PATH"
export ARM_GCC_DIR="${gcc_arm_path}"
EOF

# Also to /etc/bash.bashrc to have it in non-login shells
echo "export PATH=\"${cmake_path}/bin:${commander_path}:${gcc_arm_path}/bin:${java_path}/jre/bin:${ninja_path}:${slc_cli_path}:\$PATH\"" >> /etc/bash.bashrc
echo "export ARM_GCC_DIR=\"${gcc_arm_path}\"" >> /etc/bash.bashrc

# Set SDK and trust it
/bin/bash -lc "slc configuration --sdk $(slt where simplicity-sdk)"
/bin/bash -lc "slc signature trust --sdk $(slt where simplicity-sdk)"

# Set GCC
/bin/bash -lc "slc configuration --gcc-toolchain $(slt where gcc-arm-none-eabi)"

# Point slcd to slc daemon
cat <<EOF > /usr/local/bin/slcd
#!/bin/bash
exec "${slc_cli_path}/slc" --daemon --daemon-only "\$@"
EOF
chmod +x /usr/local/bin/slcd
