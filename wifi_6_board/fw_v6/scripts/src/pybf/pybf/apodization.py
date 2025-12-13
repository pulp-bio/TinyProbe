"""
   Copyright (C) 2020 ETH Zurich. All rights reserved.

   Author: Sergei Vostrikov, ETH Zurich

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
from numba import jit

# Calculate 'field of view' receive apodization (or expanding aperture)
# Output: array with the size of (n_pixels x n_elements)
def calc_fov_receive_apodization(num_of_elements, 
                                 elements_coords, 
                                 pixels_coords,
                                 alpha_fov_degree = 45,
                                 channel_reduction = None):

    n_elements = elements_coords.shape[1]
    n_pixels = pixels_coords.shape[1]
    elements_x = elements_coords[0,:]

    # for each FP, compute the apodization weight for each element...
    apod_weights = np.zeros((n_pixels, n_elements), dtype=np.float32)

    # Precompute hanning windows with size from 1 to  num_of_elements
    hann_win = []
    for hann in range(0, num_of_elements + 1):
        hann_win.append(np.hanning(hann))

    # Choose z axis data for al the points
    # and calculate a half of effective aperture size
    tan_alpha = np.tan(np.radians(alpha_fov_degree/2))
    delta_x = pixels_coords[1, :] * tan_alpha

    # Calculate minimum and maximum effective aperture position for each pixel points
    x_aperture_max = np.maximum(elements_x.min(), pixels_coords[0,:] - delta_x)
    x_aperture_min = np.minimum(elements_x.max(), pixels_coords[0,:] + delta_x)

    # Calculate apodization 
    for n in range(0, n_pixels):
        active_elements = np.logical_and(elements_x >= x_aperture_max[n], elements_x <= x_aperture_min[n])
        apod_weights[n, np.where(active_elements)] = hann_win[np.count_nonzero(active_elements)]

    # Mask out certain channels
    if (channel_reduction is not None):
        channel_mask = np.zeros((n_elements), dtype=np.float32)

        # channel_mask[0] = 1
        # channel_mask[-1] = 1
        # channel_mask[::channel_reduction] = 1
        ch_nr = apod_weights.shape[1]
        start_i = np.ceil((ch_nr - channel_reduction)/2)
        stop_i = start_i + channel_reduction
        channel_mask[int(start_i):int(stop_i)] = 1

        apod_weights = np.multiply(apod_weights, channel_mask)

    return  apod_weights.astype(np.float32)