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

import numpy as np

from ...runtime.parser import parse_bitstream
from .config import ProtocolExampleConfig


def parse_data(data: bytes, config: ProtocolExampleConfig) -> np.ndarray:
    num_shots = config.fpga.num_shots * config.acquisition.num_frames
    num_lanes = len(config.fpga.lvds_lanes)
    result = parse_bitstream(
        data,
        num_shots,
        config.fpga.fifo_depth,
        num_lanes,
        block_length=config.transport.bulk_packet_size_bytes
        + 2,  # account for 2 byte header in each packet
        # strip_headers=False,
    )
    result_remapped = np.empty_like(result)
    result_remapped[:, ::2] = result[:, num_lanes:][:, ::-1]
    result_remapped[:, 1::2] = result[:, :num_lanes]
    return result_remapped


def parse_shot(
    data: bytes,
    config: ProtocolExampleConfig,
    *,
    segment_index: int | None = None,
) -> np.ndarray:
    num_lanes = len(config.fpga.lvds_lanes)
    result = parse_bitstream(
        data,
        1,
        config.fpga.fifo_depth,
        num_lanes,
        block_length=config.transport.bulk_packet_size_bytes + 2,
    )
    result_remapped = np.empty_like(result)
    result_remapped[:, ::2] = result[:, num_lanes:][:, ::-1]
    result_remapped[:, 1::2] = result[:, :num_lanes]
    return result_remapped[0]
