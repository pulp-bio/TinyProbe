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

from pybf.scripts.visualize_image_dataset import visualize_image_dataset
from pybf.scripts.beamformer_cartesian_realtime import BFCartesianRealTime

# Constants
LATERAL_PIXEL_DENSITY_DEFAULT = 5
ALPHA_FOV_APOD_ANGLE_DEFAULT = 50
DB_RANGE_DEFAULT = 40
IMAGE_RESOLUTION_DEFAULT = [100, 100]

class BFGlobalMVBF(BFCartesianRealTime):

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
                 channel_reduction=None):

        super(BFGlobalMVBF, self).__init__(f_sampling, tx_strategy, transducer_obj,
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

        # Beamform the data using selected BF-core
    def beamform(self, rf_data, numba_active=False):

        print('Beamforming...')
        print (' ')
        start_time = time.time()

        acqs_to_process = [x for x in range(self._tx_delays_samples.shape[0])]

        # Allocate the data
        das_out = np.zeros((len(acqs_to_process), self._pixels_coords.shape[1]), dtype = np.complex128)

        # Check length
        # If 2D array is given and we need to process a single acquisition
        # then reshape the array
        if len(rf_data.shape) == 2 and len(acqs_to_process) == 1:
            rf_data_reshaped = rf_data.reshape((1, rf_data.shape[0], rf_data.shape[1]))
        # If we have more than one acquisition and dimensions are aligned do nothing
        elif len(rf_data.shape) == 3 and len(acqs_to_process) == rf_data.shape[0]:
            rf_data_reshaped = rf_data
        else:
            print('Input data shape ', rf_data.shape, ' is incorrect.')

        # Iterate over acquisitions
        for i in acqs_to_process:

            rf_data_proc = self._preprocess_data(rf_data_reshaped[i, :, :])

            rf_data_proc_trans = np.transpose(rf_data_proc)

            # Summ up Tx and RX delays
            delays_samples = self._rx_delays_samples + self._tx_delays_samples[i, :]
                                    
            das_out[i,:] = self._delay_and_sum(rf_data_in=rf_data_proc_trans, delays_idx=delays_samples.reshape(1, delays_samples.shape[0], -1))

        # Coherent compounding
        das_out_compound = np.sum(das_out[acqs_to_process, :], axis = 0)

        # Print execution time
        print('Time of execution: %s seconds' % (time.time() - start_time))

        return das_out_compound.reshape(self._image_res[1], self._image_res[0])

    # Perform delay and sum operation with numpy
    # Input: rf_data_in of shape (n_samples x n_elements)
    # delays_idx of shape (n_modes x n_elements x n_points)
    def _delay_and_sum(self, rf_data_in, delays_idx):

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
        # MVBF prototype goes here

        channel_reduction = self.channel_reduction
        ch_nr = n_elements
        start_i = int(np.ceil((ch_nr - channel_reduction)/2))
        stop_i = int(start_i + channel_reduction)

        mvbf_data = rf_data[fancy_idx_samples, fancy_idx_channels][0,:,start_i:stop_i]

        # Filter irrelevant data
        data_mask = self._apod[:,start_i:stop_i]
        filter_arr = []
        for i in range(0, data_mask.shape[0]):
            if (np.sum(data_mask[i,:]) == 0):
                filter_arr.append(False)
            else:
                filter_arr.append(True)
        mvbf_data = mvbf_data[filter_arr,:]

        R = np.cov(mvbf_data, rowvar=False)
        # Diagonal loading
        R = R + np.identity(channel_reduction) * np.trace(R) #  * 1/(700*channel_reduction)

        ones_vect = np.ones(channel_reduction)
        R_inv = np.linalg.inv(R)

        numerator   = np.matmul(R_inv, ones_vect.T) # vector N=nr_channels
        denominator = np.sum(np.matmul(R_inv, ones_vect.T)) # scalar - normalisation

        weights_mvbf_red = numerator / denominator

        weights_mvbf = np.zeros(n_elements, dtype=np.complex128)
        weights_mvbf[start_i:stop_i] = weights_mvbf_red

        #TEST
        

        from matplotlib import colors, cm, pyplot as plt
        fig, ax = plt.subplots(1, 1,figsize=(10,10))
        ax.plot(np.abs(weights_mvbf))
        # plt.show()
        fig.savefig('weights_distr.png')

        self._apod[self._apod > 0] = 1
        weights_mvbf = weights_mvbf * self._apod
        #######################################################################


        das_out = np.sum(np.multiply(rf_data[fancy_idx_samples, fancy_idx_channels], weights_mvbf), axis = -1)

        # Output shape: (n_modes x n_points)
        return das_out