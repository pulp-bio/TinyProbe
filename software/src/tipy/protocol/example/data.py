"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Cedric Hirschi, ETH Zurich
    - Federico Villani, ETH Zurich

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
from .config import LANE_PACKET_BYTES, SAMPLES_PER_LANE_PACKET, ProtocolExampleConfig


def _parse_frames(
    data: bytes, config: ProtocolExampleConfig, num_frames: int
) -> np.ndarray:
    num_lanes = len(set(config.fpga.lvds_lanes))
    packet_length = LANE_PACKET_BYTES + 2
    expected_bytes = num_frames * num_lanes * packet_length
    if len(data) != expected_bytes:
        raise ValueError(
            f"Expected {expected_bytes} bytes of lane packets, got {len(data)}"
        )

    # The FPGA zero-pads each lane independently to 1,000 bytes. Decode the
    # full lane stride, then remove the per-lane padding after unpacking.
    result = parse_bitstream(
        data,
        num_frames,
        SAMPLES_PER_LANE_PACKET,
        num_lanes,
        block_length=packet_length,
    )[..., : config.fpga.fifo_depth]
    result_remapped = np.empty_like(result)
    result_remapped[:, ::2] = result[:, num_lanes:][:, ::-1]
    result_remapped[:, 1::2] = result[:, :num_lanes]
    return result_remapped


def parse_data(data: bytes, config: ProtocolExampleConfig) -> np.ndarray:
    return _parse_frames(data, config, config.acquisition.num_frames)


def parse_shot(
    data: bytes,
    config: ProtocolExampleConfig,
    *,
    segment_index: int | None = None,
) -> np.ndarray:
    return _parse_frames(data, config, 1)[0]
