"""
   Copyright (C) 2021 ETH Zurich. All rights reserved.

   Author: Wolfgang Boettcher, ETH Zurich

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

# Basic libraries
import numpy as np
from os.path import dirname, abspath
import sys
import time

# Import pybf modules
from pybf.pybf.io_interfaces import ImageSaver
from pybf.pybf.image_settings import ImageSettings
from pybf.pybf.delay_calc import calc_propagation_delays
from pybf.pybf.delay_calc import convert_time_to_samples
from pybf.pybf.apodization import calc_fov_receive_apodization
from pybf.pybf.signal_processing import demodulate_decimate
from pybf.pybf.signal_processing import interpolate_modulate
from pybf.pybf.signal_processing import filter_band_pass
from pybf.pybf.signal_processing import hilbert_interpolate

# from pybf.scripts.visualize_image_dataset import visualize_image_dataset
from pybf.scripts.beamformer_cartesian_realtime import BFCartesianRealTime

# Constants
LATERAL_PIXEL_DENSITY_DEFAULT = 5
ALPHA_FOV_APOD_ANGLE_DEFAULT = 50
DB_RANGE_DEFAULT = 40
IMAGE_RESOLUTION_DEFAULT = [100, 100]

class BFMVBFdcr(BFCartesianRealTime):

    def __init__(self,
                 f_sampling,
                 tx_strategy,
                 transducer_obj,
                 decimation_factor,
                 interpolation_factor,
                 image_res,
                 img_config_obj,
                 db_range=DB_RANGE_DEFAULT,
                 start_time=None,
                 correction_time_shift=None,
                 alpha_fov_apod=ALPHA_FOV_APOD_ANGLE_DEFAULT,
                 bp_filter_params=None,
                 envelope_detector='I_Q',
                 picmus_dataset=False,
                 channel_reduction=None,
                 window_width=16,
                 is_approx_inv = False):

        super(BFMVBFdcr, self).__init__(f_sampling, tx_strategy, transducer_obj,
                 decimation_factor, interpolation_factor, image_res, 
                 img_config_obj,db_range, start_time,
                 correction_time_shift,
                 alpha_fov_apod,
                 bp_filter_params,
                 envelope_detector,
                 picmus_dataset,
                 channel_reduction=channel_reduction,
                 is_inherited=False)
        
        self.channel_reduction = channel_reduction
        self.window_width = window_width
        self.start_i = 0
        self.stop_i = 0
        self.inv_approx = is_approx_inv

        # Record info for FPGA implementation
        self.coeff_max = 0
        self.coeff_min = 0

        # Beamform the data using selected BF-core
    def beamform(self, rf_data, numba_active=False):
        acqs_to_process = [x for x in range(self._tx_delays_samples.shape[0])]

        # Check length
        # This class needs a 3D array as data from multiple beams is required
        if len(rf_data.shape) == 3 and len(acqs_to_process) == rf_data.shape[0]:
            rf_data_reshaped = rf_data
        else:
            print('Input data shape ', rf_data.shape, ' is incorrect.')

        # Iterate over acquisitions
        # Put all data in one array
        # This is not the most efficient way in RAM terms but allows for a cleaner code
        rf_pre_bf = []
        for i in acqs_to_process:
            rf_data_proc = self._preprocess_data(rf_data_reshaped[i, :, :])
            rf_data_proc_trans = np.transpose(rf_data_proc)
            # Sum up Tx and RX delays
            delays_samples = self._rx_delays_samples + self._tx_delays_samples[i, :]                                    
            rf_pre_bf_item = self._pre_bf(rf_data_in=rf_data_proc_trans, delays_idx=delays_samples.reshape(1, delays_samples.shape[0], -1))
            rf_pre_bf.append(rf_pre_bf_item)
        rf_pre_bf = np.asarray(rf_pre_bf)

        # DCR-MVBF
        print('Beamforming...')
        print (' ')
        start_time = time.time()
        dcr_out = self._dcr_beamform(rf_pre_bf)

        # Print execution time
        print('Time of execution: %s seconds' % (time.time() - start_time))

        return dcr_out.reshape(self._image_res[1], self._image_res[0])

    # Perform delay and sum operation with numpy
    # Input: rf_data_in of shape (n_samples x n_elements)
    # delays_idx of shape (n_modes x n_elements x n_points)
    def _pre_bf(self, rf_data_in, delays_idx):
        n_elements = rf_data_in.shape[1]
        n_modes = delays_idx.shape[0]
        n_points = delays_idx.shape[2]

        # Add one zero sample for data array (in the end)
        rf_data_shape = rf_data_in.shape
        rf_data = np.zeros((rf_data_shape[0] + 1, rf_data_shape[1]), dtype=np.complex64)
        rf_data[:rf_data_shape[0],:rf_data_shape[1]] = rf_data_in

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
        fancy_idx_samples = np.transpose(delays_idx, axes = [0, 2, 1])

        # Make the delay and sum operation by selecting the samples
        # using fancy indexing,
        # multiplying by apodization weights (optional)
        # and then summing them up along the last axis

        #######################################################################
        channel_reduction = self.channel_reduction
        ch_nr = n_elements
        self.start_i = int(np.ceil((ch_nr - channel_reduction)/2))
        self.stop_i = int(self.start_i + channel_reduction)
        mvbf_data = rf_data[fancy_idx_samples, fancy_idx_channels][0,:,self.start_i:self.stop_i]

        return mvbf_data

    def _dcr_beamform(self, data_array):
        L = data_array.shape[0]
        mvbf_res = np.zeros(data_array.shape[1], dtype=np.complex64)
        # Determine if pixels are in the transducer array
        data_mask = self._apod[:,self.start_i:self.stop_i]

        for i in range(data_array.shape[1]):
            # Check if pixel is in the transducer ray:
            # Skip irrelevant points
            if (np.sum(data_mask[i,:]) == 0):
                continue

            # Sum transducer respones of each transmission
            u = np.sum(data_array[:, i, :], axis=1)

            # Create snapshots
            s = []
            for k in range(data_array.shape[2]):
                s_item = np.sum(data_array[:, i, :], axis=1) - data_array[:, i, k]
                s.append(s_item)
            corr_array = np.asarray(s)

            # Calculate cov matrix
            ones_vect = np.ones(L)
            # Cov matrix
            corr_matrix = np.zeros((L,L), dtype=np.complex64)
            for y in range(0, corr_array.shape[0]):
                corr_matr_y = np.outer(np.conj(corr_array[y,:]), corr_array[y,:])
                corr_matrix = corr_matrix + corr_matr_y

            if self.inv_approx is False:
                R_inv = np.linalg.inv(corr_matrix + np.identity(L) * np.trace(corr_matrix) * 1/(1*L) )


            # # Approx. Inversion
            if self.inv_approx is True:
                diag_elem = np.diagonal(corr_matrix)
                diag_elem_inv = 1/diag_elem
                R_inv = diag_elem_inv * np.identity(corr_matrix.shape[0])

            # Record for FPGA implementation
            # self.coeff_max = np.max((np.max(np.diagonal(diag_elem2 * np.identity(L))), self.coeff_max))
            # self.coeff_min = np.min((np.min(np.diagonal(diag_elem2 * np.identity(L))), self.coeff_min))

            numerator   = np.matmul(R_inv, ones_vect.T) # vector N=nr_channels
            denominator = np.sum(np.matmul(R_inv, ones_vect.T)) # scalar - normalisation

            w_tilda = numerator / denominator

            mvbf_res[i] = np.sum(w_tilda.T * u) 

        return mvbf_res