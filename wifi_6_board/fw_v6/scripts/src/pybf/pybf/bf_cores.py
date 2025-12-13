"""
Copyright (C) 2020 ETH Zurich. All rights reserved.

Author: Sergei Vostrikov, ETH Zurich
        Cedric Hirschi, ETH Zurich

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
from numba import jit, prange
# import cupy as cp
# import warp as wp
# import taichi as ti
# import taichi.math as tm


# Initialize Warp
# wp.init()
# # Initialize Taichi
# ti.init(arch=ti.gpu, fast_math=True, kernel_profiler=True)


# Perform delay and sum operation with numba
# Input: rf_data_in of shape (n_samples x n_elements)
# delays_idx of shape (n_modes x n_elements x n_points)
# apod_weights of shape (n_points x n_elements)
@jit(nopython=True, parallel=True, nogil=True)
def delay_and_sum_numba(rf_data_in, delays_idx, apod_weights=None):
    n_elements = rf_data_in.shape[1]
    n_modes = delays_idx.shape[0]
    n_points = delays_idx.shape[2]

    # Allocate array
    das_out = np.zeros((n_modes, n_points), dtype=np.complex64)

    # Iterate over modes, points, elements
    for i in range(n_modes):
        for j in prange(n_points):
            for k in range(n_elements):
                if delays_idx[i, k, j] <= rf_data_in.shape[0] - 1:
                    if apod_weights is None:
                        das_out[i, j] += rf_data_in[delays_idx[i, k, j], k]
                    else:
                        das_out[i, j] += (
                            rf_data_in[delays_idx[i, k, j], k] * apod_weights[j, k]
                        )

    return das_out


# Perform delay and sum operation with numpy
# Input: rf_data_in of shape (n_samples x n_elements)
# delays_idx of shape (n_modes x n_elements x n_points)
def delay_and_sum_numpy(rf_data_in, delays_idx, apod_weights=None):
    n_elements = rf_data_in.shape[1]
    n_modes = delays_idx.shape[0]
    n_points = delays_idx.shape[2]

    # Add one zero sample for data array (in the end)
    rf_data_shape = rf_data_in.shape
    rf_data = np.zeros((rf_data_shape[0] + 1, rf_data_shape[1]), dtype=np.complex64)
    rf_data[: rf_data_shape[0], : rf_data_shape[1]] = rf_data_in

    # If delay index exceeds the input data array dimensions,
    # write -1 (it will point to 0 element)
    delays_idx[delays_idx >= rf_data_shape[0] - 1] = -1

    # Choose the right samples for each channel and point
    # using numpy fancy indexing

    # Create array for fancy indexing of channels
    # of size (n_modes x n_points x n_elements)
    # The last two dimensions are transposed to fit the rf_data format
    fancy_idx_channels = np.arange(0, n_elements)
    fancy_idx_channels = np.tile(fancy_idx_channels, (n_modes, n_points, 1))

    # Create array for fancy indexing of samples
    # of size (n_modes x n_points x n_elements)
    # The last two dimensions are transposed to fit the rf_data format
    fancy_idx_samples = np.transpose(delays_idx, axes=[0, 2, 1])

    # Make the delay and sum operation by selecting the samples
    # using fancy indexing,
    # multiplying by apodization weights (optional)
    # and then summing them up along the last axis

    if apod_weights is None:
        das_out = np.sum(rf_data[fancy_idx_samples, fancy_idx_channels], axis=-1)
    else:
        das_out = np.sum(
            np.multiply(rf_data[fancy_idx_samples, fancy_idx_channels], apod_weights),
            axis=-1,
        )

    # Output shape: (n_modes x n_points)
    return das_out


# def delay_and_sum_cupy(rf_data_in, delays_idx, apod_weights=None):
#     """
#     GPU-accelerated Delay-and-Sum using CuPy.

#     Parameters
#     ----------
#     rf_data_in : array_like, shape (n_samples, n_elements)
#         Input RF data on the host.
#     delays_idx : array_like of ints, shape (n_modes, n_elements, n_points)
#         Delay indices per mode/element/point.
#     apod_weights : array_like, shape (n_points, n_elements), optional
#         Apodization weights.

#     Returns
#     -------
#     out : ndarray, shape (n_modes, n_points)
#         Beamformed output on the host.
#     """
#     # Move inputs to GPU
#     rf = cp.asarray(rf_data_in, dtype=cp.complex64)
#     delays = cp.asarray(delays_idx, dtype=cp.int32)

#     # Dimensions
#     n_samples, n_elements = rf.shape
#     n_modes, _, n_points = delays.shape

#     # 1) Pad one zero row
#     rf = cp.vstack(
#         [rf, cp.zeros((1, n_elements), dtype=rf.dtype)]
#     )  # → (n_samples+1, n_elements)

#     # 2) Clip out-of-bounds delays to point at that last zero row
#     safe_idx = cp.clip(delays, 0, n_samples)  # (n_modes, n_elements, n_points)

#     # 3) Broadcast RF array to (n_modes, n_samples+1, n_elements)
#     arr = cp.broadcast_to(rf[None, :, :], (n_modes, rf.shape[0], n_elements))

#     # 4) Transpose indices to (n_modes, n_points, n_elements)
#     idx = safe_idx.transpose(0, 2, 1)

#     # 5) Gather delayed samples: (n_modes, n_points, n_elements)
#     samples = cp.take_along_axis(arr, idx, axis=1)

#     # 6) Apply apodization if provided
#     if apod_weights is not None:
#         # Move and align weights: (1, n_points, n_elements)
#         w = cp.asarray(apod_weights, dtype=samples.dtype)[None, :, :]
#         samples = samples * w

#     # 7) Sum across elements → (n_modes, n_points)
#     out_gpu = samples.sum(axis=2)

#     # 8) Bring result back to host
#     return cp.asnumpy(out_gpu)


# # Warp kernel for Delay-and-Sum (DAS)
# @wp.kernel
# def das_warp_kernel(
#     rf_real: wp.array2d(dtype=float),  # (n_samples, n_elements) # type: ignore
#     rf_imag: wp.array2d(dtype=float),  # (n_samples, n_elements) # type: ignore
#     delays: wp.array3d(dtype=int),  # (n_modes, n_elements, n_points) # type: ignore
#     apo: wp.array2d(dtype=float),  # (n_points, n_elements) # type: ignore
#     out_real: wp.array2d(dtype=float),  # (n_modes, n_points) # type: ignore
#     out_imag: wp.array2d(dtype=float),  # (n_modes, n_points) # type: ignore
#     n_samples: int,
#     n_elements: int,
#     use_apo: bool,
# ):
#     # Get 2D thread indices
#     mode, pt = wp.tid()  # type: ignore

#     acc_r = float(0.0)
#     acc_i = float(0.0)

#     # Sum over elements
#     for ele in range(n_elements):
#         idx = delays[mode, ele, pt]
#         if 0 <= idx < n_samples:
#             r = rf_real[idx, ele]
#             i = rf_imag[idx, ele]
#             # Use explicit if since warp kernels disallow ternary expressions
#             w = 1.0
#             if use_apo:
#                 w = apo[pt, ele]
#             acc_r += r * w
#             acc_i += i * w

#     out_real[mode, pt] = acc_r
#     out_imag[mode, pt] = acc_i


# def delay_and_sum_warp(rf_data_in, delays_idx, apod_weights=None):
#     """
#     Warp-accelerated DAS.

#     rf_data_in : (n_samples, n_elements) complex64 on host
#     delays_idx : (n_modes, n_elements, n_points) int32 on host
#     apod_weights: (n_points, n_elements) float32 on host or None
#     """
#     # --- host->device
#     rf_real = wp.array(rf_data_in.real.astype(np.float32))
#     rf_imag = wp.array(rf_data_in.imag.astype(np.float32))
#     delays = wp.array(delays_idx.astype(np.int32))

#     n_modes, n_elements, n_points = delays_idx.shape
#     n_samples, _ = rf_data_in.shape

#     if apod_weights is None:
#         apo = wp.zeros((n_points, n_elements), dtype=float)
#         use_apo = False
#     else:
#         apo = wp.array(apod_weights.astype(np.float32))
#         use_apo = True

#     # allocate outputs on device
#     out_r = wp.zeros((n_modes, n_points), dtype=float)
#     out_i = wp.zeros((n_modes, n_points), dtype=float)

#     # launch 2D grid: (modes x points)
#     wp.launch(
#         kernel=das_warp_kernel,
#         dim=(n_modes, n_points, 1),
#         inputs=[
#             rf_real,
#             rf_imag,
#             delays,
#             apo,
#             out_r,
#             out_i,
#             n_samples,
#             n_elements,
#             use_apo,
#         ],
#     )
#     wp.synchronize()

#     # device->host and recombine
#     real = out_r.numpy().astype(np.float32)
#     imag = out_i.numpy().astype(np.float32)
#     return (real + 1j * imag).astype(np.complex64)


# ti_rf = ti.Vector.field(2, dtype=ti.f16, shape=(1, 1))
# ti_delay = ti.field(dtype=ti.i32, shape=(1, 1, 1))
# ti_apo = ti.field(dtype=ti.f16, shape=(1, 1))
# ti_out = ti.Vector.field(2, dtype=ti.f16, shape=(1, 1))

# ti_max_idx: int = 0
# ti_nelem: int = 0
# ti_nmodes: int = 0
# ti_npts: int = 0


# @ti.kernel
# def _das_unweighted_kernel():
#     # for i in range(ti_nmodes):
#     #     for j in range(ti_npts):
#     #         for k in range(ti_nelem):
#     #             idx = ti_delay[i, k, j]
#     #             if idx <= ti_max_idx:
#     #                 ti_out[i, j] += ti_rf[idx, k]
#     # flatten (mode,point) → a single index p

#     # ti.loop_config(parallelize=16)
#     # for p in range(ti_nmodes * ti_npts):
#     #     mode = p // ti_npts
#     #     pt = p % ti_npts
#     #     acc = ti.Vector([0.0, 0.0])
#     #     # sum over elements
#     #     for e in range(ti_nelem):
#     #         idx = ti_delay[mode, e, pt]
#     #         if idx <= ti_max_idx:
#     #             acc += ti_rf[idx, e]
#     #     ti_out[mode, pt] = acc

#     # expose a 2D grid of (mode, pt)
#     for mode, pt in ti.ndrange(ti_nmodes, ti_npts):
#         acc = ti.Vector([0.0, 0.0])
#         # unroll over a small, fixed number of elements
#         for e in ti.static(range(ti_nelem)):
#             idx = ti_delay[mode, e, pt]
#             if idx <= ti_max_idx:
#                 # coalesced load from ti_rf[e, idx]
#                 acc += ti_rf[e, idx]
#         ti_out[mode, pt] = acc


# @ti.kernel
# def _das_weighted_kernel():
#     # for i in range(ti_nmodes):
#     #     for j in range(ti_npts):
#     #         for k in range(ti_nelem):
#     #             idx = ti_delay[i, k, j]
#     #             if idx <= ti_max_idx:
#     #                 w = ti_apo[j, k]
#     #                 ti_out[i, j] += ti_rf[idx, k] * w

#     # ti.loop_config(parallelize=16)
#     # for p in range(ti_nmodes * ti_npts):
#     #     mode = p // ti_npts
#     #     pt = p % ti_npts
#     #     acc = ti.Vector([0.0, 0.0])
#     #     for e in range(ti_nelem):
#     #         idx = ti_delay[mode, e, pt]
#     #         if idx <= ti_max_idx:
#     #             w = ti_apo[pt, e]
#     #             acc += ti_rf[idx, e] * w
#     #     ti_out[mode, pt] = acc

#     for mode, pt in ti.ndrange(ti_nmodes, ti_npts):
#         acc = ti.Vector([0.0, 0.0])
#         # unroll over a small, fixed number of elements
#         for e in ti.static(range(ti_nelem)):
#             idx = ti_delay[mode, e, pt]
#             if idx <= ti_max_idx:
#                 # coalesced load from ti_rf[e, idx]
#                 acc += ti_rf[e, idx] * ti_apo[pt, e]
#         ti_out[mode, pt] = acc


# def delay_and_sum_taichi(
#     rf_data_in: np.ndarray,
#     delays_idx: np.ndarray,
#     apod_weights: np.ndarray | None = None,
# ):
#     # print("Preparing Taichi arrays for delay and sum...")
#     # time_start = time.perf_counter()
#     n_samples, n_elements = rf_data_in.shape
#     n_modes, _, n_points = delays_idx.shape

#     global ti_rf, ti_delay, ti_apo, ti_out

#     # pack complex into last axis
#     rf_mat = np.stack([rf_data_in.real, rf_data_in.imag], axis=-1)
#     # transpose so shape=(n_elements, n_samples, 2) for coalescing
#     rf_mat_t = rf_mat.transpose(1, 0, 2)

#     if ti_rf.shape != (n_elements, n_samples):
#         # store as f16 to reduce bandwidth; cast back in‐kernel
#         print("Allocating new ti_rf array with shape:", (n_elements, n_samples))
#         ti_rf = ti.Vector.field(2, dtype=ti.f16, shape=(n_elements, n_samples))
#     ti_rf.from_numpy(rf_mat_t.astype(np.float16))

#     if ti_delay.shape != (n_modes, n_elements, n_points):
#         print(
#             "Allocating new ti_delay array with shape:", (n_modes, n_elements, n_points)
#         )
#         ti_delay = ti.field(dtype=ti.i32, shape=(n_modes, n_elements, n_points))
#     ti_delay.from_numpy(delays_idx.astype(np.int32))

#     if apod_weights is not None:
#         if ti_apo.shape != (n_points, n_elements):
#             print("Allocating new ti_apo array with shape:", (n_points, n_elements))
#             ti_apo = ti.field(dtype=ti.f16, shape=(n_points, n_elements))
#         ti_apo.from_numpy(apod_weights.astype(np.float16))

#     if ti_out.shape != (n_modes, n_points):
#         print("Allocating new ti_out array with shape:", (n_modes, n_points))
#         ti_out = ti.Vector.field(2, dtype=ti.f16, shape=(n_modes, n_points))

#     global ti_max_idx, ti_nelem, ti_nmodes, ti_npts

#     ti_max_idx = n_samples - 1
#     ti_nelem = n_elements
#     ti_nmodes = n_modes
#     ti_npts = n_points

#     # print(f"  {(time.perf_counter() - time_start) * 1e3:.2f} ms")
#     # time_start = time.perf_counter()

#     if ti_apo is not None:
#         # print("Starting Taichi weighted delay and sum kernel...")
#         _das_weighted_kernel()
#     else:
#         # print("Starting Taichi unweighted delay and sum kernel...")
#         _das_unweighted_kernel()

#     ti.sync()  # ensure all operations are done
#     # print(f"  {(time.perf_counter() - time_start) * 1e3:.2f} ms")
#     ti.profiler.print_kernel_profiler_info("trace")
#     ti.profiler.clear_kernel_profiler_info()

#     out_np = ti_out.to_numpy()  # (modes, points, 2)
#     return out_np[..., 0] + 1j * out_np[..., 1]
