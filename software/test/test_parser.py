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
import pytest

from tipy.runtime.parser import parse_bitstream

from .common import OUTPUT_DIR, load_binary, load_config

BUFFER_SIZE = 4000
HEADER_LENGTH = 2
BLOCK_LENGTH = BUFFER_SIZE + HEADER_LENGTH


class TestParser:
    def test_parse_bitstream(self):
        data = load_binary("string_1cm/string_1cm.bin")
        config = load_config("string_1cm/string_1cm.json")

        data_headers_removed = []
        for i in range(len(data)):
            if (i % BLOCK_LENGTH) < HEADER_LENGTH:
                continue
            data_headers_removed.append(data[i])
        data = bytes(data_headers_removed)

        num_shots = config["fpga"]["num_shots"]
        fifo_depth = config["fpga"]["fifo_depth"]
        num_lvds_lanes = len(config["fpga"]["lvds_lanes"])
        num_channels = num_lvds_lanes * 2

        out = parse_bitstream(
            data,
            num_shots=num_shots,
            fifo_depth=fifo_depth,
            num_lvds_lanes=num_lvds_lanes,
            strip_headers=False,
        )

        np.save(OUTPUT_DIR / "parsed_output.npy", out)

        assert out.shape == (num_shots, num_channels, fifo_depth)

    def test_parse_bitstream_allzeros(self):
        num_shots = 10
        fifo_depth = 1000
        num_lvds_lanes = 4
        num_channels = num_lvds_lanes * 2

        data_length = (fifo_depth * 2 * 10) // 8 * num_lvds_lanes * num_shots
        data = bytes([0x00] * data_length)

        out = parse_bitstream(
            data,
            num_shots=num_shots,
            fifo_depth=fifo_depth,
            num_lvds_lanes=num_lvds_lanes,
            strip_headers=False,
        )

        assert out.shape == (num_shots, num_channels, fifo_depth)
        assert np.all(out == 512)

    def test_parse_bitstream_allzeros_headers(self):
        num_shots = 10
        fifo_depth = 1000
        num_lvds_lanes = 4
        num_channels = num_lvds_lanes * 2

        data_length = (fifo_depth * 2 * 10) // 8 * num_lvds_lanes * num_shots

        num_blocks = data_length // BUFFER_SIZE + 1
        data_with_headers = bytearray()
        for i in range(num_blocks):
            data_with_headers += i.to_bytes(2, "big")  # Header
            data_with_headers += bytes([0x00] * BUFFER_SIZE)  # Data
        data = bytes(data_with_headers)

        out = parse_bitstream(
            data,
            num_shots=num_shots,
            fifo_depth=fifo_depth,
            num_lvds_lanes=num_lvds_lanes,
        )

        assert out.shape == (num_shots, num_channels, fifo_depth)
        assert np.all(out == 512)

    def test_parse_bitstream_allones(self):
        num_shots = 10
        fifo_depth = 1000
        num_lvds_lanes = 4
        num_channels = num_lvds_lanes * 2

        data_length = (fifo_depth * 2 * 10) // 8 * num_lvds_lanes * num_shots
        data = bytes([0xFF] * data_length)

        out = parse_bitstream(
            data,
            num_shots=num_shots,
            fifo_depth=fifo_depth,
            num_lvds_lanes=num_lvds_lanes,
            strip_headers=False,
        )

        assert out.shape == (num_shots, num_channels, fifo_depth)
        assert np.all(out == 511)

    def test_parse_bitstream_alternating(self):
        num_shots = 10
        fifo_depth = 1000
        num_lvds_lanes = 4
        num_channels = num_lvds_lanes * 2

        data_length = (fifo_depth * 2 * 10) // 8 * num_lvds_lanes * num_shots
        data = bytes([0xF8, 0x3E, 0x0F, 0x83, 0xE0] * (data_length // 5))

        out = parse_bitstream(
            data,
            num_shots=num_shots,
            fifo_depth=fifo_depth,
            num_lvds_lanes=num_lvds_lanes,
            strip_headers=False,
        )

        assert out.shape == (num_shots, num_channels, fifo_depth)
        assert np.all(out == 480)

    def test_parse_bitstream_invalid_length(self):
        num_shots = 10
        fifo_depth = 1000
        num_lvds_lanes = 4

        data_length = (fifo_depth * 2 * 10) // 8 * num_lvds_lanes * num_shots + 1
        data = bytes([0x00] * data_length)

        with pytest.raises(ValueError):
            parse_bitstream(
                data,
                num_shots=num_shots,
                fifo_depth=fifo_depth,
                num_lvds_lanes=num_lvds_lanes,
                strip_headers=False,
            )
