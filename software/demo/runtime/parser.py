"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Cedric Hirschi, ETH Zurich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from tipy.runtime.parser import parse_bitstream

raw_data = (Path(__file__).parent / "example_bitstream.bin").read_bytes()


parsed_data = parse_bitstream(
    raw_data,
    num_shots=5,
    fifo_depth=500,
    num_lvds_lanes=16,
    block_length=4002,
    header_length=2,
    strip_headers=True,
)
print(
    f"Parsed data: {len(parsed_data)} shots, {len(parsed_data[0])} channels with {len(parsed_data[0][0])} samples each"
)

plt.figure()
plt.imshow(
    parsed_data[3], aspect="auto", cmap="gray"
)  # We just plot the 4th shot as an example
plt.savefig(Path(__file__).parent / "example_bitstream.png")
