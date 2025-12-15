import numpy as np
from matplotlib import pyplot as plt
from math import *
from numba import njit

MAX_FIFO_SIZE = 2048
BUFFER_SIZE = 1000
HEADER_LENGTH = 2
NUM_BITS = 10


def parse_bitstream_original(
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

    assert correct_dim <= bytes_arr.shape[0], "Not enough data in the input byte array"

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


def parse_bitstream_numpy(
    data_raw: bytes | np.ndarray,
    num_shots: int,
    num_frames: int,
    fifo_depth: int,
    lvds_lanes: list[int] | np.ndarray,
) -> np.ndarray:
    data_headers_removed = []
    for i in range(len(data_raw)):
        if (i % (BUFFER_SIZE + HEADER_LENGTH)) < HEADER_LENGTH:
            continue
        data_headers_removed.append(data_raw[i])

    data_raw = bytes(data_headers_removed)[1:]
    data_raw = data_raw[: len(data_raw) - (len(data_raw) % NUM_BITS)]
    data = np.frombuffer(data_raw, dtype=np.uint8)

    data_bits = np.unpackbits(data, axis=-1, bitorder="big")
    data_bits = data_bits.reshape((-1, NUM_BITS)).astype(np.uint16)

    weights = (1 << np.arange(NUM_BITS - 1, -1, -1)).astype(np.uint16)
    data_stitched = (data_bits * weights).sum(axis=1).astype(np.uint16)
    data = data_stitched

    bytes_per_acq = len(data) // (num_frames * num_shots)
    data = data[: len(data) - (len(data) % bytes_per_acq)].reshape((-1, bytes_per_acq))
    data = data[:, : fifo_depth * len(lvds_lanes) * 2]

    return data[
        :,
        : data.shape[1]
        - (data.shape[1] % (num_shots * num_frames * len(lvds_lanes) * 2)),
    ].reshape((num_shots, num_frames, len(lvds_lanes) * 2, -1))


@njit
def parse_bitstream_numba(
    data: np.ndarray,  # uint8 array, NOT bytes
    num_shots: int,
    num_frames: int,
    fifo_depth: int,
    lvds_lanes: np.ndarray,  # int array
) -> np.ndarray:
    # ------------------------------------------------------------
    # Remove headers
    # ------------------------------------------------------------
    total_block = BUFFER_SIZE + HEADER_LENGTH

    # count valid bytes
    valid_count = 0
    for i in range(data.size):
        if (i % total_block) >= HEADER_LENGTH:
            valid_count += 1

    tmp = np.empty(valid_count, dtype=np.uint8)
    idx = 0
    for i in range(data.size):
        if (i % total_block) >= HEADER_LENGTH:
            tmp[idx] = data[i]
            idx += 1

    # drop first byte
    tmp = tmp[1:]

    # ------------------------------------------------------------
    # Trim to NUM_BITS alignment
    # ------------------------------------------------------------
    usable_len = tmp.size - (tmp.size % NUM_BITS)
    tmp = tmp[:usable_len]

    # ------------------------------------------------------------
    # Unpack bits
    # ------------------------------------------------------------
    bit_count = tmp.size * 8
    bits = np.empty(bit_count, dtype=np.uint8)

    bidx = 0
    for i in range(tmp.size):
        v = tmp[i]
        for b in range(8):
            bits[bidx + b] = (v >> (7 - b)) & 1
        bidx += 8

    # reshape to NUM_BITS
    n_words = bits.size // NUM_BITS
    bits = bits[: n_words * NUM_BITS]
    bits = bits.reshape((n_words, NUM_BITS))

    # ------------------------------------------------------------
    # Stitch NUM_BITS → uint16
    # ------------------------------------------------------------
    out = np.zeros(n_words, dtype=np.uint16)

    for i in range(n_words):
        acc = 0
        for b in range(NUM_BITS):
            acc |= bits[i, b] << (NUM_BITS - 1 - b)
        out[i] = acc

    data = out

    # ------------------------------------------------------------
    # Frame / shot reshaping
    # ------------------------------------------------------------
    bytes_per_acq = data.size // (num_frames * num_shots)
    usable = bytes_per_acq * num_frames * num_shots
    data = data[:usable]

    data = data.reshape((-1, bytes_per_acq))

    lane_count = lvds_lanes.size
    lane_bytes = fifo_depth * lane_count * 2
    data = data[:, :lane_bytes]

    block = num_shots * num_frames * lane_count * 2
    usable_cols = data.shape[1] - (data.shape[1] % block)

    data = data[:, :usable_cols]
    data = np.ascontiguousarray(data)

    return data.reshape(num_shots, num_frames, lane_count * 2, -1)
