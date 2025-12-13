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

# %%
from os.path import abspath
from os.path import dirname as up
import numpy as np
import sys

# %%
path_to_lib = up(up(up(up(up(abspath(__file__))))))
sys.path.insert(0, path_to_lib)
from pybf.pybf.io_interfaces import DataLoader
from pybf.scripts.beamformer_cartesian_realtime import BFCartesianRealTime
from pybf.scripts.beamformer_global_mvbf import BFGlobalMVBF
from pybf.pybf.image_settings import ImageSettings
from pybf.pybf.visualization import plot_image
from pybf.scripts.picmus_eval import PicmusEval


# %%
dataset_path_contrast = path_to_lib + '/pybf/tests/data/Picmus/contrast_speckle/rf_dataset.hdf5'
dataset_path_resolution = path_to_lib + '/pybf/tests/data/Picmus/resolution_distorsion/rf_dataset.hdf5'


# %%
data_loader_obj_contrast = DataLoader(dataset_path_contrast)
data_loader_obj_resolution = DataLoader(dataset_path_resolution)

# %% [markdown]
# ### Image settings

# %%
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
                           data_loader_obj_resolution.transducer)

### Specify preprocessing parameters for RF data ###

decimation_factor = 1
interpolation_factor = 10

### Specify TX strategy and Apodization parameters ###

start_time = 0
correction_time_shift = 0

alpha_fov_apod = 40

# 1 Plane waves with inclination angle 0
# tx_strategy = ['PW_75_16', [16]]
tx_strategy = ['PW_1_0', [0]]

### Specify Sampling Frequency ###

SAMPLING_FREQ = 20.832 * (10 ** 6)

filters_params = [1 * 10 **6, 8 * 10 **6, 0.5 * 10 **6]

# %% [markdown]
# ### Instantiate beamformer for single Plane Wave with 0 inclination angle

# %%
bf = BFGlobalMVBF(data_loader_obj_resolution.f_sampling,
                         tx_strategy,
                         data_loader_obj_resolution.transducer,
                         decimation_factor,
                         interpolation_factor,
                         img_res,
                         img_config,
                         start_time=start_time,
                         correction_time_shift=correction_time_shift,
                         alpha_fov_apod=alpha_fov_apod,
                         bp_filter_params=filters_params,
                         envelope_detector='hilbert',
                         picmus_dataset=True,
                         channel_reduction=32)

# %% [markdown]
# ### Beamform

# %%
rf_data = data_loader_obj_resolution.get_rf_data(0, 37)
img_data = bf.beamform(rf_data, numba_active=False)

# Eval tests
eval_obj = PicmusEval(img_data, bf)
circle_pos = np.asarray([[-0.00022,0.01867, 0.002, 0.0005],
                            [-0.0105, 0.0281, 0.007, 0.0039]])

CNR_values = eval_obj.evaluate_circ_contrast(circle_pos)


scatterer_pos = np.asarray([[-0.001, 0.018, 0.001, 0.001],
                            [-0.0104, 0.0375, 0.001, 0.001],
                            [0.0001, 0.0375, 0.001, 0.001]])

FWHM_x, FWHM_y = eval_obj.evaluate_FWHM(scatterer_pos)

print("CNR values are [dB]:")
print(str(CNR_values) + "\n")
print("x-axis FWHM values are [m]:")
print(str(FWHM_x))
print("z-axis FWHM values are [m]:")
print(str(FWHM_y))

# %% [markdown]
# ### Visualize PW 0
plot_image(np.abs(img_data), 
           scatters_coords_xz=None,
           elements_coords_xz=None,
           framework='matplotlib',
           title='Original Image (PW_0)MV-dl',
           image_x_range=image_x_range,
           image_z_range=image_z_range,
           db_range=db_range,
           colorscale='Greys',
           save_fig=True, 
           show=True,
           path_to_save='.')