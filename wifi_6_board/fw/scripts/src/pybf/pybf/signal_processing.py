"""
   Copyright (C) 2020 ETH Zurich. All rights reserved.

   Authors: Sergei Vostrikov and Pascal Hager, ETH Zurich

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
from scipy import signal as ss
import math

# Demodulate Decimate (real - > complex IQ (or baseband signal) decimated)
# Each column in input data represents the time sample, 
# Each row stands for channel
def demodulate_decimate(data, f_sampling, f_carrier, decimation_factor, koff = 0):

    # Create time array for the input samples
    time_arr = (np.arange(0, data.shape[1], dtype=np.float32) + koff) / f_sampling

    # Create complex carrier wave
    carrier = 2 * np.exp(-1.j * 2 * np.pi * f_carrier * time_arr)

    # Demodulate the input data by multiplying it with complex carrier 
    # data_demod = data * np.tile(carrier.reshape(1, carrier.shape[0]), (data.shape[0], 1))
    data_demod = data * np.tile(carrier.reshape(1, -1), (data.shape[0], 1))

    # Decimate the data by the factor decimation_factor
    data_DD = ss.decimate(data_demod, decimation_factor, zero_phase=True)

    # out = data_DD[:,0:math.floor(data.shape[1]/decimation_factor)]
    out = data_DD

    return out.astype(np.complex64)

# Demodulate Decimate (complex IQ decimated -> complex analytical signal (interpolated))
# Each column in input data represents the time sample, 
# Each row stands for channel
def interpolate_modulate(data_IQ, f_sampling, f_carrier, interpolation_factor, toff = 0):

    # Calculate the sampling frequency after interpolation
    f_interpolated = f_sampling * interpolation_factor

    # Interpolate the data using Fourier method along the columns
    data_IQ_interp = ss.resample(data_IQ, data_IQ.shape[1] * interpolation_factor, axis=-1)

    # Create time array for the interpolated samples
    time_arr = np.arange(0, data_IQ_interp.shape[1]) / (f_interpolated) + toff

    # Create complex carrier wave
    carrier = np.exp(1.j * 2 * np.pi * f_carrier * time_arr)

    # Multiply the interpolated data by the complex carrier wave 
    data_out = data_IQ_interp * np.tile(carrier.reshape(1, -1), (data_IQ_interp.shape[0], 1))

    return data_out

# Apply Hilbert transform and then interpolate the data
def  hilbert_interpolate(data_RF, f_sampling, interpolation_factor):

    # Hilbert transform
    data_hilbert = ss.hilbert(data_RF, axis=-1)

    # Interpolate the data using Fourier method along the columns
    data_hilbert_interp = ss.resample(data_hilbert, data_hilbert.shape[1] * interpolation_factor, axis=-1)

    return data_hilbert_interp

# Bandpass filter
# transition width is the same for both low and high cutoff frequencies
def filter_band_pass(data, f_sampling, f_low_cutoff, f_high_cutoff, trans_width, n_taps = 101):
    # Make filter
    b = ss.remez(n_taps, 
                [0, f_low_cutoff - trans_width, f_low_cutoff, f_high_cutoff, f_high_cutoff + trans_width, f_sampling/2],
                [0, 1,  0], 
                Hz=f_sampling, 
                maxiter=2500)
    a = 1

    return ss.filtfilt(b, a, data)