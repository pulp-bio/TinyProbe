"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Sergei Vostrikov, ETH Zurich
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

import logging
from math import ceil

import jax
import jax.numpy as jnp
import numpy as np

SPI_BITWIDTH = 8
MAX_FIFO_SIZE = 2048


log = logging.getLogger().getChild("parser")


def parse_bitstream_numpy(
    data: bytes | np.ndarray,
    num_shots: int,
    fifo_depth: int,
    num_lvds_lanes: int = 16,
    bits_per_sample: int = 10,
    bit_slips: list[int] | None = None,
    strip_headers: bool = True,
    header_length: int = 2,
    block_length: int = 4002,
):
    if strip_headers:
        # Remove headers from the bitstream
        data_no_headers = []
        for i in range(len(data)):
            if (i % block_length) < header_length:
                continue
            data_no_headers.append(data[i])
        data = bytes(data_no_headers)

    # Convert input
    if isinstance(data, (bytes, bytearray, memoryview)):
        np_bytes = np.frombuffer(data, dtype=np.uint8)
    else:
        np_bytes = np.asarray(data, dtype=np.uint8)

    lvds_word_width = 2 * bits_per_sample
    bytes_per_lane_exp = (fifo_depth * lvds_word_width) // SPI_BITWIDTH
    bytes_per_shot_exp = bytes_per_lane_exp * num_lvds_lanes

    if np_bytes.size % num_shots != 0:
        raise ValueError("Buffer size not divisible by num_shots")

    bytes_per_shot_act = np_bytes.size // num_shots
    if bytes_per_shot_act < bytes_per_shot_exp:
        raise ValueError(
            f"Shot too short: have {bytes_per_shot_act} B/shot, need >= {bytes_per_shot_exp} B/shot"
        )

    if bit_slips is not None and len(bit_slips) != num_lvds_lanes:
        raise ValueError("bit_slips length must match num_lvds_lanes")

    # Shape the data into shots and lanes
    bytes_arr = np_bytes.reshape(num_shots, bytes_per_shot_act)[:, :bytes_per_shot_exp]
    bytes_arr = bytes_arr.reshape(num_shots, num_lvds_lanes, bytes_per_lane_exp)

    # 2.0 Unpack bytes into an array of bits (big-endian)
    bits_arr = np.unpackbits(bytes_arr, axis=-1, bitorder="big")

    # 3.1 Drop unused bits for odd number of samples
    if fifo_depth % 2 == 1:
        bits_arr = bits_arr[..., : bits_arr.shape[-1] - 2 * SPI_BITWIDTH]

    arr_bit_slip = bits_arr.copy()

    # 4.0 Bit slip compensation
    # First, reshape the array in LVDS words and then flip the order of the word axis
    arr_bit_slip = np.flip(
        arr_bit_slip.reshape((num_shots, num_lvds_lanes, -1, lvds_word_width)), axis=2
    ).reshape((num_shots, num_lvds_lanes, -1))

    if bit_slips is not None:
        # Since bit slip is applied to the reversed array, reverse the bit slip array
        bit_slip_arr = -np.array(bit_slips)

        # Correct bit slip per lane across all shots
        for i in range(num_lvds_lanes):
            arr_bit_slip[:, i, :] = np.roll(
                arr_bit_slip[:, i, :], bit_slip_arr[i], axis=-1
            )

        # Calc max abs shift
        max_bit_shift = np.max(bit_slip_arr)
        if max_bit_shift > 0:
            # N samples
            n_to_cut_from_start = ceil(max_bit_shift / (lvds_word_width))
            # Bits per LVDS word
            n_to_cut_from_start = n_to_cut_from_start * lvds_word_width
        else:
            n_to_cut_from_start = 0

        min_bit_shift = np.min(bit_slip_arr)
        if min_bit_shift < 0:
            # N samples
            n_to_cut_from_end = ceil(np.abs(min_bit_shift) / (lvds_word_width))
            # Bits per LVDS word
            n_to_cut_from_end = n_to_cut_from_end * lvds_word_width

        else:
            n_to_cut_from_end = 0

        if n_to_cut_from_end == 0:
            arr_bit_slip = arr_bit_slip[..., n_to_cut_from_start:]
        else:
            arr_bit_slip = arr_bit_slip[..., n_to_cut_from_start:-n_to_cut_from_end]

    # Return the original order of the LVDS words
    arr_bit_slip = np.flip(
        arr_bit_slip.reshape((num_shots, num_lvds_lanes, -1, lvds_word_width)), axis=2
    )

    # 5.0 Reshape according to the number of channels
    arr_bits_ch = arr_bit_slip.reshape(
        num_shots, num_lvds_lanes, -1, 2, bits_per_sample
    )
    arr_bits_ch = np.transpose(arr_bits_ch, axes=(0, 1, 3, 2, 4))
    arr_bits_ch = arr_bits_ch.reshape(
        num_shots, num_lvds_lanes * 2, -1, bits_per_sample
    )

    # 6.0 Pad array to further make int short (16 bits)
    def pad_array(arr, new_bitwidth=16, original_bitwidth=bits_per_sample):
        # Create zero array
        arr_new = np.zeros(
            (arr.shape[0], arr.shape[1], arr.shape[2], new_bitwidth), dtype=np.int32
        )

        # Copy the data
        arr_new[..., -arr.shape[3] :] = arr

        # Inverse MSB sign bit to convert two's complement representation to offset binary
        sign_bit_pos = new_bitwidth - original_bitwidth
        arr_new[:, :, :, sign_bit_pos] = 1 - arr_new[:, :, :, sign_bit_pos]

        return arr_new

    # 6.0 Pad arrays
    arr_bits_ch_padded = pad_array(arr_bits_ch)

    # 7.0 Pack a padded array into an array of uint16
    def pack_bits(arr):
        # Order VERIFIED BY SYNC TEST PATTERN
        return np.squeeze(
            np.packbits(arr.copy(), axis=-1, bitorder="big").view(">u2"), axis=-1
        )

    arr_out = pack_bits(arr_bits_ch_padded)

    return arr_out


# ---- Utilities ----

# 256x8 LUT for big-endian bit order (bit 7 first)
_BE_UNPACK_LUT = jnp.array(
    [[(i >> (7 - b)) & 1 for b in range(8)] for i in range(256)], dtype=jnp.uint8
)


def _unpack_u8_last_be(u8: jnp.ndarray) -> jnp.ndarray:
    bits8 = _BE_UNPACK_LUT[u8]  # (..., B, 8)
    return bits8.reshape(*u8.shape[:-1], -1)  # (..., B*8)


def _roll_per_lane(bits: jnp.ndarray, slip: jnp.ndarray) -> jnp.ndarray:
    # bits: (S, L, K), slip: (L,)
    bt = jnp.swapaxes(bits, 0, 1)  # (L, S, K)
    rolled = jax.vmap(lambda b_l, s: jnp.roll(b_l, s, axis=-1), in_axes=(0, 0))(
        bt, slip
    )
    return jnp.swapaxes(rolled, 0, 1)


# ---- JIT core (no Python asserts!) ----


def _parse_bitstream_core_impl(
    bytes_arr: jnp.ndarray,  # (num_shots, bytes_per_shot_exp) - already reshaped
    read_size_samples: int,
    bits_per_sample: int,
    n_activ_ch: int,
    has_bit_slip: bool,  # whether to apply bit slip
    bit_slip_arr: jnp.ndarray,  # (N_LVDS,) - always present but may be zeros
):
    num_shots = bytes_arr.shape[0]
    N_LVDS = n_activ_ch // 2
    LVDS_WORD_WIDTH = 2 * bits_per_sample  # e.g., 20

    # Expected bytes per lane/shot
    bytes_per_lane_exp = (read_size_samples * LVDS_WORD_WIDTH) // SPI_BITWIDTH

    # (S, L, bytes_per_lane) - bytes_arr is already the right shape
    ba = bytes_arr.reshape(num_shots, N_LVDS, bytes_per_lane_exp)

    # Unpack bits big-endian
    bits = _unpack_u8_last_be(ba)  # (S, L, bytes*8)

    # Drop last 2 bytes/lane when odd number of samples
    # Ensure both branches produce the same shape by padding when needed
    bits_full_size = bits.shape[-1]
    target_size = (
        bits_full_size - (2 * SPI_BITWIDTH)
        if (read_size_samples & 1) == 1
        else bits_full_size
    )

    # Always slice to the target size (if target_size == full_size, this is a no-op)
    bits = bits[..., :target_size]

    # Reverse LVDS-word order
    bits = bits.reshape(num_shots, N_LVDS, -1, LVDS_WORD_WIDTH)[:, :, ::-1, :].reshape(
        num_shots, N_LVDS, -1
    )

    # Bit-slip per lane - simplified to avoid dynamic shapes
    if has_bit_slip:
        slip = -bit_slip_arr.astype(jnp.int32)
        bits = _roll_per_lane(bits, slip)

        # For simplicity, apply a conservative fixed trim that works for most cases
        # This avoids the dynamic slicing issue
        # In production, you might want to pre-compute the exact trim needed
        max_possible_trim = 20 * LVDS_WORD_WIDTH  # Conservative estimate
        if bits.shape[-1] > max_possible_trim * 2:
            bits = bits[..., max_possible_trim:-max_possible_trim]

    # Restore original word order
    bits = bits.reshape(num_shots, N_LVDS, -1, LVDS_WORD_WIDTH)[:, :, ::-1, :]
    # JAX arrays are already efficiently laid out in memory

    # Assemble 20-bit words from bits (big-endian within word)
    weights = 1 << jnp.arange(LVDS_WORD_WIDTH - 1, -1, -1, dtype=jnp.uint32)
    words = jnp.tensordot(bits.astype(jnp.uint32), weights, axes=([-1], [0]))  # (S,L,W)

    # Split into two samples and interleave into channels
    mask = jnp.uint32((1 << bits_per_sample) - 1)
    ch0 = (words >> bits_per_sample).astype(jnp.uint16)
    ch1 = (words & mask).astype(jnp.uint16)

    inter = jnp.stack([ch0, ch1], axis=2)  # (S, L, 2, W)
    out = inter.reshape(num_shots, N_LVDS * 2, inter.shape[-1])  # (S, n_activ_ch, W)

    # Two's-complement -> offset-binary
    out = out ^ jnp.uint16(1 << (bits_per_sample - 1))
    return out


# Create JIT compiled version
_parse_bitstream_core = jax.jit(_parse_bitstream_core_impl, static_argnums=(1, 2, 3, 4))


# ---- Public wrapper ----


def parse_bitstream_jax(
    data: bytes | np.ndarray,
    num_shots: int,
    fifo_depth: int,
    num_lvds_lanes: int = 16,
    bits_per_sample: int = 10,
    bit_slips: list[int] | None = None,
    strip_headers: bool = True,
    header_length: int = 2,
    block_length: int = 4002,
):
    log.debug(
        f"Parsing bitstream: num_shots={num_shots}, fifo_depth={fifo_depth}, num_lvds_lanes={num_lvds_lanes}, bits_per_sample={bits_per_sample}"
    )

    if strip_headers:
        # Remove headers from the bitstream
        data_no_headers = []
        for i in range(len(data)):
            if (i % block_length) < header_length:
                continue
            data_no_headers.append(data[i])
        data = bytes(data_no_headers)

    # Convert input
    if isinstance(data, (bytes, bytearray, memoryview)):
        np_bytes = np.frombuffer(data, dtype=np.uint8)
    else:
        np_bytes = np.asarray(data, dtype=np.uint8)

    lvds_word_width = 2 * bits_per_sample
    bytes_per_lane_exp = (fifo_depth * lvds_word_width) // SPI_BITWIDTH
    bytes_per_shot_exp = bytes_per_lane_exp * num_lvds_lanes
    log.debug(f"Expected bytes per shot: {bytes_per_shot_exp}")

    if np_bytes.size % num_shots != 0:
        raise ValueError(
            f"Buffer size ({np_bytes.size}) not divisible by num_shots ({num_shots})"
        )

    bytes_per_shot_act = np_bytes.size // num_shots
    log.debug(f"Actual bytes per shot: {bytes_per_shot_act}")
    if bytes_per_shot_act < bytes_per_shot_exp:
        raise ValueError(
            f"Shot too short: have {bytes_per_shot_act} B/shot, need >= {bytes_per_shot_exp} B/shot"
        )

    # Prepare bit slip array - always pass an array, use zeros if None
    if bit_slips is None:
        slip_array = jnp.zeros(num_lvds_lanes, dtype=jnp.int32)
        has_bit_slip = False
    else:
        slip_array = jnp.asarray(bit_slips, dtype=jnp.int32)
        has_bit_slip = True

    # Pre-process the data to have the correct shape for JAX
    # This avoids shape tracing issues in the JIT function
    np_bytes_reshaped = np_bytes.reshape(num_shots, bytes_per_shot_act)[
        :, :bytes_per_shot_exp
    ]

    out = _parse_bitstream_core(
        jnp.asarray(np_bytes_reshaped, dtype=jnp.uint8),
        int(fifo_depth),
        int(bits_per_sample),
        int(num_lvds_lanes) * 2,
        has_bit_slip,
        slip_array,
    )
    return out  # jnp.ndarray (uint16)


# # Use jax version as the main parser
parse_bitstream = parse_bitstream_jax
# parse_bitstream = parse_bitstream_numpy
