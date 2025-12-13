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

import os
from os.path import abspath
from os.path import dirname as up
import numpy as np
import sys

path_to_lib = up(up(up(up(up(abspath(__file__))))))
sys.path.insert(0, path_to_lib)

from pybf.pybf.io_interfaces import DataLoader
from pybf.scripts.beamformer_DAS_ref import BFCartesianReference
from pybf.scripts.beamformer_mvbf_spatial_smooth import BFMVBFspatial
from pybf.scripts.beamformer_mvbf_DCR import BFMVBFdcr
from pybf.pybf.image_settings import ImageSettings
from pybf.pybf.visualization import plot_image
from pybf.scripts.picmus_eval import PicmusEval

dataset_path_contrast = path_to_lib + '/pybf/tests/data/Picmus/contrast_speckle/rf_dataset.hdf5'

data_loader_obj_contrast = DataLoader(dataset_path_contrast)

### Specify Image settings and create corresponding object ###

img_res = [400, 600]
image_x_range = [-0.019, 0.019]
image_z_range = [0.005, 0.05]

db_range = 50

LATERAL_PIXEL_DENSITY_DEFAULT = 5

img_config = ImageSettings(image_x_range[0],
                           image_x_range[1],
                           image_z_range[0],
                           image_z_range[1],
                           LATERAL_PIXEL_DENSITY_DEFAULT,
                           data_loader_obj_contrast.transducer)

### Specify preprocessing parameters for RF data ###

decimation_factor = 1
interpolation_factor = 10

### Specify TX strategy and Apodization parameters ###

start_time = 0
correction_time_shift = 0

alpha_fov_apod = 40

# 1 Plane waves with inclination angle 0
# tx_strategy = ['PW_75_16', [16]]
tx_strategy = ['PW_4_2', [data_loader_obj_contrast.tx_strategy[1][33], data_loader_obj_contrast.tx_strategy[1][37], data_loader_obj_contrast.tx_strategy[1][38], data_loader_obj_contrast.tx_strategy[1][42]]]
rf_data_shape = (len(tx_strategy[1]),) + data_loader_obj_contrast.get_rf_data(0, 0).shape
rf_data = np.zeros(rf_data_shape)
inclin_index = np.asarray([33, 37, 38, 42])
for i in range(rf_data.shape[0]):
    rf_data[i, :, :] = data_loader_obj_contrast.get_rf_data(0, inclin_index[i])

### Specify Sampling Frequency ###

SAMPLING_FREQ = 20.832 * (10 ** 6)

filters_params = [1 * 10 **6, 8 * 10 **6, 0.5 * 10 **6]

bf = BFCartesianReference(data_loader_obj_contrast.f_sampling,
                         tx_strategy,
                         data_loader_obj_contrast.transducer,
                         decimation_factor,
                         interpolation_factor,
                         img_res,
                         img_config,
                         start_time=start_time,
                         correction_time_shift=correction_time_shift,
                         alpha_fov_apod=alpha_fov_apod,
                         bp_filter_params=filters_params,
                         envelope_detector='I_Q',
                         picmus_dataset=True,
                         channel_reduction=32)

bf2 = BFMVBFspatial(data_loader_obj_contrast.f_sampling,
                         tx_strategy,
                         data_loader_obj_contrast.transducer,
                         decimation_factor,
                         interpolation_factor,
                         img_res,
                         img_config,
                         start_time=start_time,
                         correction_time_shift=correction_time_shift,
                         alpha_fov_apod=alpha_fov_apod,
                         bp_filter_params=filters_params,
                         envelope_detector='I_Q',
                         picmus_dataset=True,
                         channel_reduction=32,
                         window_width=8)

img_data = bf.beamform(rf_data, numba_active=True)
img_data2 = bf2.beamform(rf_data, numba_active=False)      

# Eval tests
eval_obj = PicmusEval(img_data, bf)
circle_pos = np.asarray([[-0.00043, 0.01492, 0.0035, 0.00172],
                            [-0.00043, 0.04279, 0.0035, 0.00172],
                            [-0.0072, 0.02829, 0.0063, 0.00315]])
                            
CNR_values = eval_obj.evaluate_circ_contrast(circle_pos)

print("CNR values are [dB]:")
print(str(CNR_values) + "\n")

# Eval tests
eval_obj2 = PicmusEval(img_data2, bf)
CNR_values2 = eval_obj2.evaluate_circ_contrast(circle_pos)

print("CNR values are [dB]:")
print(str(CNR_values2) + "\n")

plot_image(np.abs(img_data), 
               scatters_coords_xz=None,
               elements_coords_xz=None,
               framework='matplotlib',
               title='DAS_128_4',
               image_x_range=image_x_range,
               image_z_range=image_z_range,
               db_range=db_range,
               colorscale='Greys',
               save_fig=True, 
               show=True,
               path_to_save='.')

plot_image(np.abs(img_data2), 
               scatters_coords_xz=None,
               elements_coords_xz=None,
               framework='matplotlib',
               title='MVBFss_128_4',
               image_x_range=image_x_range,
               image_z_range=image_z_range,
               db_range=db_range,
               colorscale='Greys',
               save_fig=True, 
               show=True,
               path_to_save='.')