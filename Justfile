# Copyright (C) 2026 ETH Zurich. All rights reserved.
#
# Authors:
#     - Cedric Hirschi, ETH Zurich
#     - Federico Villani, ETH Zurich
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

mod software
mod container
mod firmware
mod fpga

embgen := "uv run embgen"
config_source_path := "config"
config_codegen_path := config_source_path / "codegen"
sw_source_path := "software/src/tipy"
regmap_output := sw_source_path / "hardware/fpga/regmap.py"
regmap_header := "firmware/user/tp/hal/regmap_fpga.h"

# List available recipes
default:
    @just --list --list-submodules

# Generate firmware and Python interfaces from YAML configuration files
codegen: _proto _regmap
    sed -i 's/from \.regmap_base/from ..regmap_base/' {{ regmap_output }}
    uv run ruff format {{ sw_source_path }}

# Run pre-commit hooks on all files using prek
pre-commit:
    uv run prek run -a

# Serve the documentation locally
docs_serve:
    uv run mkdocs serve

# Remove generated regmap files
clean:
    rm -f {{ regmap_output }}

[private]
_proto:
    {{ embgen }} -s nanopb {{ config_codegen_path }}/methods.yml -un -o {{ config_codegen_path }}/
    {{ embgen }} -s nanopb {{ config_codegen_path }}/methods.yml -p -o {{ sw_source_path }}/control/
    uv run protoc \
        --python_out={{ sw_source_path }}/control/ \
        --pyi_out={{ sw_source_path }}/control/ \
        --proto_path={{ config_codegen_path }}/ \
        {{ config_codegen_path }}/methods.proto

[private]
_regmap:
    {{ embgen }} -s auto {{ config_codegen_path }}/regmap_fpga.yml -p -c -o {{ sw_source_path }}/hardware/fpga/
    # Work around the pinned embgen template shifting a 32-bit mask by 32.
    sed -i 's/(1U << 32) - 1/UINT32_MAX/g' {{ sw_source_path }}/hardware/fpga/regmap.h
    mv {{ sw_source_path }}/hardware/fpga/regmap.h {{ regmap_header }}
    mv {{ sw_source_path }}/hardware/fpga/regmap_base.py {{ sw_source_path }}/hardware/regmap_base.py
