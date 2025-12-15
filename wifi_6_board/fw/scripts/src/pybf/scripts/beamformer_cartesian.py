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

# Basic libraries
import numpy as np
from os.path import dirname, abspath
import sys
import time
import argparse

# Import pybf modules
from pybf.pybf.io_interfaces import DataLoader
from pybf.pybf.image_settings import ImageSettings
from pybf.pybf.delay_calc import calc_propagation_delays
from pybf.pybf.delay_calc import convert_time_to_samples
from pybf.pybf.apodization import calc_fov_receive_apodization
from pybf.pybf.signal_processing import demodulate_decimate
from pybf.pybf.signal_processing import interpolate_modulate
from pybf.pybf.signal_processing import filter_band_pass
from pybf.pybf.io_interfaces import ImageSaver
from pybf.pybf.bf_cores import delay_and_sum_numba, delay_and_sum_numpy
from pybf.scripts.visualize_image_dataset import visualize_image_dataset

# Constants
LATERAL_PIXEL_DENSITY_DEFAULT = 5
ALPHA_FOV_APOD_ANGLE_DEFAULT = 50
DB_RANGE_DEFAULT = 40
IMAGE_RESOLUTION_DEFAULT = [100, 100]

def beamformer_cartesian(path_to_rf_dataset,
                         decimation_factor,
                         interpolation_factor,
                         image_res,
                         image_x_range,
                         image_z_range,
                         save_images_to_hdf5=True,
                         save_lri_to_hdf5=False,
                         save_visualized_images=False,
                         show_images=False,
                         save_path=None,
                         frames_to_plot=None,
                         low_res_img_to_plot=None,
                         db_range=DB_RANGE_DEFAULT,
                         start_time=None,
                         correction_time_shift=None,
                         alpha_fov_apod=ALPHA_FOV_APOD_ANGLE_DEFAULT,
                         active_elements=None,
                         frames_to_process=[],
                         acqs_to_process=[],
                         bp_filter_params=None):

    # 1 Create DataLoader object
    print('Loading data...')
    dl = DataLoader(path_to_rf_dataset)

    # Select transducer channels for reconstruction
    if active_elements is not None:
        dl.transducer.set_active_elements(active_elements)

    # 2 Specify image settings
    lateral_pixel_density = LATERAL_PIXEL_DENSITY_DEFAULT

    img_config = ImageSettings(image_x_range[0],
                               image_x_range[1],
                               image_z_range[0],
                               image_z_range[1],
                               lateral_pixel_density, 
                               dl.transducer)

    # Calculate pixels coordinate based on desired resolution
    pixels_coords = img_config.get_pixels_coords(image_res[0], image_res[1])

    # 3 Precalculate delays
    print('Delays precalculation...')
    rx_delays, tx_delays = calc_propagation_delays(dl.tx_strategy,
                                                   dl.transducer.num_of_elements,
                                                   dl.transducer.elements_coords,
                                                   pixels_coords,
                                                   dl.transducer.speed_of_sound,
                                                   simulation_flag=dl.simulation_flag)

    # Calculate final sampling rate for preprocessed data
    f_sampling_proc = dl.f_sampling / decimation_factor * interpolation_factor

    # Convert delays from time domain to samples
    if start_time is None:
        start_time = dl.hardware.start_time

    if correction_time_shift is None:
        correction_time_shift = dl.hardware.correction_time_shift

    # Convert time delays into samples' indices
    # Incorporate correction time shift only in rx delays
    rx_delays_samples = convert_time_to_samples(rx_delays, 
                                                f_sampling_proc,
                                                start_time,
                                                correction_time_shift)

    tx_delays_samples = convert_time_to_samples(tx_delays, f_sampling_proc,0,0)

    # 4 Calculate Apodization
    print('Apodization precalculation...')
    apod = calc_fov_receive_apodization(int(dl.transducer.num_of_elements), 
                                        dl.transducer.elements_coords, 
                                        pixels_coords,
                                        alpha_fov_degree = alpha_fov_apod)

    # 5 Make the data preprocessing function
    # Demodulate decimate
    def preprocess_data(rf_data, decim_factor, interp_factor):

        if bp_filter_params is not None:
            rf_data_filt = filter_band_pass(rf_data,
                                            dl.f_sampling, 
                                            bp_filter_params[0], 
                                            bp_filter_params[1],
                                            bp_filter_params[2])
        else:
            rf_data_filt = rf_data

        rf_data_IQ = demodulate_decimate(rf_data_filt, 
                                         dl.f_sampling, 
                                         dl.transducer.f_central_hz, 
                                         decim_factor)

        rf_data_proc = interpolate_modulate(rf_data_IQ, 
                                            dl.f_sampling / decim_factor, 
                                            dl.transducer.f_central_hz, 
                                            interp_factor)

        f_sampling_proc = dl.f_sampling / decimation_factor * interpolation_factor
        return (rf_data_proc, f_sampling_proc)

    # Construct save path (save to dataset folder by default)
    if save_path is None:
        len_to_cut = len(path_to_rf_dataset.split('/')[-1])
        save_path = path_to_rf_dataset[:-1 - len_to_cut]

    # Prepare the output file for images
    if save_images_to_hdf5:
        saver = ImageSaver(save_path + '/' + 'image_dataset.hdf5')

    # 6 Beamform the data using selected BF-core and save the data
    # New empty line for progress bar
    print('Beamforming...')
    print (' ')
    start_time = time.time()

    # Allocate the data
    das_out = np.zeros((dl.num_of_acq_per_frame, pixels_coords.shape[1]), dtype = np.complex128)

    # Check the frames_to_process list
    if frames_to_process is not None:
        if len(frames_to_process) is 0:
            frames_to_process = [i for i in range(dl.num_of_frames)]
    else:
        frames_to_process = []


    # Check the acqs_to_process list
    if acqs_to_process is not None:
        if len(acqs_to_process) is 0:
            acqs_to_process = [i for i in range(dl.num_of_acq_per_frame)]
    else:
        acqs_to_process = []

    # Iterate over frames
    frame_counter = 0
    for j in frames_to_process:
        
        # Iterate over acquisitions
        for i in acqs_to_process:

            start_bf = time.time()

            # get RF data
            rf_data = dl.get_rf_data(j, i)

            # Preproces the data
            rf_data_proc,_ = preprocess_data(rf_data, 
                                             decimation_factor, 
                                             interpolation_factor)

            rf_data_proc_trans = np.transpose(rf_data_proc)

            # Summ up Tx and RX delays
            delays_samples = rx_delays_samples + tx_delays_samples[i, :]

            # Make delay and sum operation + apodization
            das_out[i,:] = delay_and_sum_numba(rf_data_proc_trans, 
                                               delays_samples.reshape(1, delays_samples.shape[0], -1), 
                                               apod_weights=apod)

        # Coherent compounding
        das_out_compound = np.sum(das_out[acqs_to_process, :], axis = 0)

        # Save images as I/Q data
        if save_images_to_hdf5:
            # Save low resolution images
            if save_lri_to_hdf5:
                saver.save_low_res_images(das_out.reshape(-1, image_res[1], image_res[0]), j, 
                                          low_res_imgs_indices = acqs_to_process)
            saver.save_high_res_image(das_out_compound.reshape(image_res[1], image_res[0]), j)
    
        # Print progress
        # Cursor up one line
        frame_counter = frame_counter + 1
        sys.stdout.write("\033[F")
        print('Frame: ', frame_counter, 
              'Progress: ', "{0:.2f}".format(frame_counter/len(frames_to_process) * 100), ' %')
        print('Time per frame: %s seconds', time.time() - start_bf)

    # Print execution time
    print('Time of execution: %s seconds' % (time.time() - start_time))

    # 7 Save image settings and close the file with images
    if save_images_to_hdf5:
        # Save Pixels and elements coordinates + resolution
        saver.save_params(pixels_coords, 
                          np.array(image_res), 
                          dl.transducer.elements_coords,
                          dl.fps)
        # Save scatters positions for simulation mode
        if dl.simulation_flag:
            saver.save_simulation_params(dl.get_scatters_pos()[[0,2],:])
        saver.close_file()

    # 8 Visualization
    print('Visualization...')

    visualize_image_dataset(save_path + '/' + 'image_dataset.hdf5',
                            save_visualized_images=save_visualized_images,
                            show_images=show_images,
                            frames_to_plot=frames_to_plot,
                            low_res_img_to_plot=low_res_img_to_plot,
                            db_range=db_range)

    print('Done.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--path_to_rf_dataset',
        type=str,
        default=' ',
        help='Path to the dataset file.')

    # Active transducers to use
    parser.add_argument(
        '--active_elements',
        type=int,
        nargs="+",
        default=None,
        help='Space separated list of active transducers.\
        "None" - use all elements specified by transducer object.')

    # Image settings
    parser.add_argument(
        '--image_x_range',
        type=float,
        nargs="+",
        default=[-0.5, 0.5],
        help='Space separated list with image x range\
        in meters "x_min x_max".')
    parser.add_argument(
        '--image_z_range',
        type=float,
        nargs="+",
        default=[0, 1],
        help='Space separated list with image z range\
        in meters "z_min z_max".')
    parser.add_argument(
        '--image_resolution',
        type=int,
        nargs="+",
        default=IMAGE_RESOLUTION_DEFAULT,
        help='Space separated list with image resolution\
         "x_res z_res".')

    # Delay calculation parameters
    parser.add_argument(
        '--start_time',
        type=float,
        default=None,
        help='Start time of the first sample in each acquisition')
    parser.add_argument(
        '--correction_time_shift',
        type=float,
        default=None,
        help='Correction time caused by pulse duration')

    # Data preprocessing parameters
    parser.add_argument(
        '--decimation_factor',
        type=int,
        default=1,
        help='Decimation factor for input data processing')
    parser.add_argument(
        '--interpolation_factor',
        type=int,
        default=1,
        help='Interpolation factor for input data processing')

    # Apodization settings
    parser.add_argument(
        '--alpha_fov_apod',
        type=float,
        default=49.0,
        help='Angle of field of view (in degrees) that is used for "expanding apertures" apodization')

    # Frames to process
    parser.add_argument(
        '--frames_to_process',
        type=int,
        nargs="+",
        default=[],
        help='Space separated list of frames to process.\
        "[]" - process all frames. "None" - process none.')

    # Acquisitions to process
    parser.add_argument(
        '--acqs_to_process',
        type=int,
        nargs="+",
        default=[],
        help='Space separated list of acuisitions to process.\
        "[]" - process all acuisitions. "None" - process none.')

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 'True', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'False', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    # Flag to save images to hdf5
    parser.add_argument(
        '--save_images_to_hdf5',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Flag to save images to separate hdf5 file.')
    parser.add_argument(
        '--save_lri_to_hdf5',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Flag to save low resolution images to hdf5 file.')

    # Parameters for visualization
    parser.add_argument(
        '--save_visualized_images',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Flag to save visualized images.')
    parser.add_argument(
        '--show_images',
        type=str2bool,
        nargs='?',
        const=True,
        default=False,
        help='Flag to save visualized images.')
    parser.add_argument(
        '--save_path',
        type=str,
        default=' ',
        help='Path to the save image dataset.')

    parser.add_argument(
        '--frames_to_plot',
        type=int,
        nargs="+",
        default=None,
        help='Space separated list of frames to plot.\
        "[]" - plot all frames. "None" - plot none.')
    parser.add_argument(
        '--low_res_img_to_plot',
        type=int,
        nargs="+",
        default=None,
        help='Space separated list of low resolution images to plot.\
        "[]" - plot all frames. "None" - plot none.')
    parser.add_argument(
        '--db_range',
        type=float,
        default=None,
        help='Decibels range for log compression of images ')
    

    FLAGS, unparsed = parser.parse_known_args()

    # Run main
    beamformer_cartesian(FLAGS.path_to_rf_dataset,
                         FLAGS.decimation_factor,
                         FLAGS.interpolation_factor,
                         FLAGS.image_resolution,
                         FLAGS.image_x_range,
                         FLAGS.image_z_range,
                         save_images_to_hdf5=FLAGS.save_images_to_hdf5,
                         save_lri_to_hdf5=FLAGS.save_lri_to_hdf5,
                         save_visualized_images=FLAGS.save_visualized_images,
                         save_path=FLAGS.save_path,
                         show_images=FLAGS.show_images,
                         frames_to_plot=FLAGS.frames_to_plot,
                         low_res_img_to_plot=FLAGS.low_res_img_to_plot,
                         db_range=FLAGS.db_range,
                         start_time=FLAGS.start_time,
                         correction_time_shift=FLAGS.correction_time_shift,
                         alpha_fov_apod=FLAGS.alpha_fov_apod,
                         active_elements=FLAGS.active_elements,
                         frames_to_process=FLAGS.frames_to_process,
                         acqs_to_process=FLAGS.acqs_to_process)