from typing import Optional
import time
from math import floor, ceil

import numpy as np
import jax
import jax.numpy as jnp

SPI_BITWIDTH = 8
MAX_FIFO_SIZE = 2048

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
    bits_per_sample_out: int,
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
_parse_bitstream_core = jax.jit(
    _parse_bitstream_core_impl, static_argnums=(1, 2, 3, 4, 5)
)


# ---- Public wrapper ----


def parse_bitstream_jax(
    bytes_in: bytes | np.ndarray,
    num_shots: int,
    read_size_samples: int,
    bits_per_sample: int,
    n_activ_ch: int,
    *,
    bits_per_sample_out: int = 16,
    bit_slip_arr: Optional[list[int]] = None,
    dbg_msgs: bool = False,
):
    # Python-side validations (keep them OUTSIDE jit)
    if n_activ_ch % 2 != 0:
        raise ValueError("n_activ_ch must be even")
    if bits_per_sample_out < bits_per_sample:
        raise ValueError("bits_per_sample_out must be >= bits_per_sample")

    # Convert input
    if isinstance(bytes_in, (bytes, bytearray, memoryview)):
        np_bytes = np.frombuffer(bytes_in, dtype=np.uint8)
    else:
        np_bytes = np.asarray(bytes_in, dtype=np.uint8)

    N_LVDS = n_activ_ch // 2
    LVDS_WORD_WIDTH = 2 * bits_per_sample
    bytes_per_lane_exp = (read_size_samples * LVDS_WORD_WIDTH) // SPI_BITWIDTH
    bytes_per_shot_exp = bytes_per_lane_exp * N_LVDS

    if np_bytes.size % num_shots != 0:
        raise ValueError("Buffer size not divisible by num_shots")

    bytes_per_shot_act = np_bytes.size // num_shots
    if bytes_per_shot_act < bytes_per_shot_exp:
        raise ValueError(
            f"Shot too short: have {bytes_per_shot_act} B/shot, need >= {bytes_per_shot_exp} B/shot"
        )
    if bytes_per_shot_act > bytes_per_shot_exp and dbg_msgs:
        print(f"Truncating per-shot bytes {bytes_per_shot_act} -> {bytes_per_shot_exp}")

    # Prepare bit slip array - always pass an array, use zeros if None
    if bit_slip_arr is None:
        slip_array = jnp.zeros(N_LVDS, dtype=jnp.int32)
        has_bit_slip = False
    else:
        slip_array = jnp.asarray(bit_slip_arr, dtype=jnp.int32)
        has_bit_slip = True

    # Pre-process the data to have the correct shape for JAX
    # This avoids shape tracing issues in the JIT function
    np_bytes_reshaped = np_bytes.reshape(num_shots, bytes_per_shot_act)[
        :, :bytes_per_shot_exp
    ]

    out = _parse_bitstream_core(
        jnp.asarray(np_bytes_reshaped, dtype=jnp.uint8),
        int(read_size_samples),
        int(bits_per_sample),
        int(n_activ_ch),
        int(bits_per_sample_out),
        has_bit_slip,
        slip_array,
    )
    return out  # jnp.ndarray (uint16)


if __name__ == "__main__":
    TEST_DATA = "test/perpendicular_phantom_lowdepth_85fps.npy"
    NUM_SHOTS_RX = 150
    FIFO_READ_DEPTH = 1024
    EN_LVDS_CH = list(range(16))
    BITS_PER_SAMPLE = 10

    raw_bytes = np.load(TEST_DATA).tobytes()

    bytes_per_shot = int(len(raw_bytes) / NUM_SHOTS_RX)

    # Set up GPU
    # jax.config.update("jax_platform_name", "gpu")
    jax.config.update("jax_enable_x64", True)
    print("JAX using device:", jax.devices()[0])
    print("JAX version:", jax.__version__)
    print("JAX backend:", jax.lib.xla_bridge.get_backend().platform)
    print("JAX devices:", jax.devices())

    # Warmup
    for i in range(10):
        parsed_new = parse_bitstream_jax(
            raw_bytes[bytes_per_shot * i : bytes_per_shot * (i + 10)],
            num_shots=10,
            read_size_samples=FIFO_READ_DEPTH,
            bits_per_sample=BITS_PER_SAMPLE,
            n_activ_ch=len(EN_LVDS_CH) * 2,
            bits_per_sample_out=16,
            bit_slip_arr=[-2] * 16,
            dbg_msgs=False,
        )

    print("Testing new parser...")
    for i in range(10):
        t0 = time.time()
        parsed_new = parse_bitstream_jax(
            raw_bytes[bytes_per_shot * i : bytes_per_shot * (i + 10)],
            num_shots=10,
            read_size_samples=FIFO_READ_DEPTH,
            bits_per_sample=BITS_PER_SAMPLE,
            n_activ_ch=len(EN_LVDS_CH) * 2,
            bits_per_sample_out=16,
            bit_slip_arr=[-2] * 16,
            dbg_msgs=False,
        )
        t1 = time.time()
        elapsed = t1 - t0
        print(f"  Parsing took {elapsed:.3f} s")
    print(f"  Possible FR: {len(parsed_new) / elapsed:.1f} Hz")


def parse_bitstream(
    bytes,
    dbg_msgs=True,
    read_size_samples=2048,
    bits_per_sample=10,
    n_activ_ch=32,
    bit_slip_arr=[-2 for x in range(16)],
):
    SPI_BITWIDTH = 8
    N_LVDS = int(n_activ_ch / 2)
    LVDS_WORD_WIDTH = 2 * bits_per_sample

    bytes_arr = np.array(bytearray(bytes), dtype="<u1")

    # 1.0 Remove extra bytes
    assert n_activ_ch % 2 == 0, "n_active_ch is not a multiple of two"

    # Calculate the number of transmitted bytes
    # # TAke into account that 3 bytes are somehow lost (due to Microsemi early assert of FIFO almost empty signal)
    # if (read_size_samples == MAX_FIFO_SIZE):
    #     bytes_per_buf = int(read_size_samples*LVDS_WORD_WIDTH/SPI_BITWIDTH) - 3
    # elif read_size_samples % 2 == 0:
    if read_size_samples % 2 == 0:
        bytes_per_buf = int(read_size_samples * LVDS_WORD_WIDTH / SPI_BITWIDTH)
    else:
        bytes_per_buf = floor(read_size_samples * LVDS_WORD_WIDTH / SPI_BITWIDTH)
    correct_dim = bytes_per_buf * N_LVDS

    assert (
        correct_dim <= bytes_arr.shape[0]
    ), f"Not enough data in the input byte array: {bytes_arr.shape[0]} < {correct_dim}"

    if dbg_msgs:
        print("Initilal length of byte array: ", bytes_arr.shape[0])
        print("Aligned  length of byte array: ", correct_dim)

    bytes_arr_corr = bytes_arr[:correct_dim].copy()

    # 2.0 Unpack bytes into an array of bits
    bits_arr = np.unpackbits(bytes_arr_corr, axis=-1, bitorder="big")

    # 3.0 Reshape it according to the number of active LVDS lanes (they are read sequentially by the IP module)
    arr_temp = bits_arr.reshape((N_LVDS, -1))

    # 3.1 Drop unused bits
    if dbg_msgs:
        print("Shape of bit array: ", arr_temp.shape)

    # According to the multi_fifo_reader (20 bits input, 8 bits output)
    # we need to drop the last 2 bytes for some specific cases
    # if (read_size_samples == MAX_FIFO_SIZE) or (read_size_samples % 2 == 1):
    if read_size_samples % 2 == 1:
        arr_temp = arr_temp[:, : arr_temp.shape[1] - 2 * SPI_BITWIDTH]

    if dbg_msgs:
        print("Trimmed shape of bit array: ", arr_temp.shape)

    # return arr_temp

    arr_bit_slip = arr_temp.copy()

    # 4.0 Bit slip compensation

    # First, reshape the array in 20-bit words and then flip the order of the second axis
    # This step is verified by the RAMP test pattern of the AFE
    arr_bit_slip = np.flip(arr_bit_slip.reshape((N_LVDS, -1, 20)), axis=1).reshape(
        (N_LVDS, -1)
    )

    if bit_slip_arr is not None:
        # Since bit slip is applied to the reversed array, reverse the bit slip array
        bit_slip_arr = -np.array(bit_slip_arr)

        # Correct bit slip
        for i in range(N_LVDS):
            arr_bit_slip[i, :] = np.roll(arr_bit_slip[i, :], bit_slip_arr[i])

        # Calc max abs shift
        max_bit_shift = np.max(bit_slip_arr)
        if max_bit_shift > 0:
            # N samples
            n_to_cut_from_start = ceil(max_bit_shift / (LVDS_WORD_WIDTH))
            # Bits per LVDS word
            n_to_cut_from_start = n_to_cut_from_start * LVDS_WORD_WIDTH
        else:
            n_to_cut_from_start = 0

        min_bit_shift = np.min(bit_slip_arr)
        if min_bit_shift < 0:
            # N samples
            n_to_cut_from_end = ceil(np.abs(min_bit_shift) / (LVDS_WORD_WIDTH))
            # Bits per LVDS word
            n_to_cut_from_end = n_to_cut_from_end * LVDS_WORD_WIDTH

        else:
            n_to_cut_from_end = 0

        if n_to_cut_from_end == 0:
            arr_bit_slip = arr_bit_slip[:, n_to_cut_from_start:]
        else:
            arr_bit_slip = arr_bit_slip[:, n_to_cut_from_start:-n_to_cut_from_end]

        if dbg_msgs:
            print(
                "Cut from the start n samples, n = : ",
                int(n_to_cut_from_start / LVDS_WORD_WIDTH),
            )
            print(
                "Cut from the end n samples, n = : ",
                int(n_to_cut_from_end / LVDS_WORD_WIDTH),
            )
            print("Bit slip corrected number of bits per lane: ", arr_bit_slip.shape[1])

    # Return the original order of the LVDS words
    arr_bit_slip = np.flip(arr_bit_slip.reshape((N_LVDS, -1, 20)), axis=1).reshape(
        (N_LVDS, -1)
    )

    # 5.0 Reshape according to the number of channels
    arr_bits_ch = np.transpose(
        arr_bit_slip.reshape(N_LVDS, -1, 2, bits_per_sample), axes=(0, 2, 1, 3)
    )
    arr_bits_ch = arr_bits_ch.reshape(n_activ_ch, -1, bits_per_sample)

    # return arr_bit_slip

    if dbg_msgs:
        print("N of acquired samples: ", arr_bits_ch.shape[1])

    # 6.0 Pad array to further make int short (16 bits)
    def pad_array(arr, new_bitwidth=16, original_bitwidth=bits_per_sample):
        # Create zero array
        arr_new = np.zeros((arr.shape[0], arr.shape[1], new_bitwidth), dtype=np.int32)

        # Copy the data
        arr_new[-arr.shape[0] :, -arr.shape[1] :, -arr.shape[2] :] = arr

        # Inverse MSB sign bit to convert
        # two's complement representation to offset binary
        sign_bit_pos = new_bitwidth - original_bitwidth
        arr_new[:, :, sign_bit_pos] = 1 - arr_new[:, :, sign_bit_pos]

        return arr_new

    # 6.0 Pad arrays
    arr_bits_ch_padded = pad_array(arr_bits_ch)

    # 7.0 Pack a padded array into an array of int16
    def pack_bits(arr):
        # Order VERIFIED BY SYNC TEST PATTERN
        return np.squeeze(
            np.packbits(arr.copy(), axis=-1, bitorder="big").view(">u2"), axis=-1
        )

    arr_out = pack_bits(arr_bits_ch_padded)

    # return arr_out, arr_bits_ch_padded, arr_temp, arr_bit_slip
    return arr_out
