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

from os.path import abspath
from os.path import dirname as up
import sys

# Insert path to pybf library to system path
path_to_lib = up(up(up(up(up(abspath(__file__))))))
sys.path.insert(0, path_to_lib)

from pybf.scripts.beamformer_cartesian import beamformer_cartesian
from pybf.scripts.visualize_image_dataset import visualize_image_dataset

if __name__ == '__main__':

    # Following dataset released under CC BY license (see data/README.md for details) 
    path_to_dataset = path_to_lib + '/pybf/tests/data/rf_dataset.hdf5'

    decimation_factor = 1
    interpolation_factor = 10

    img_res = [400, 600]
    image_x_range = [-0.022, 0.022]
    image_z_range = [0.0014784, 0.04]
    # Save images
    save_images_to_hdf5 = True
    # Save low resolution images
    save_lri_to_hdf5 = True

    # For this test start_time and correction_time_shift is specified
    # by the dataset that contains simulated data.
    start_time = None
    correction_time_shift = None
    alpha_fov_apod = 50

    # All elements are active
    active_elements = None

    # All frames and all acquisitions
    frames_to_process = []
    acqs_to_process = []

    # Plot only first frame (HRI + LRI)
    save_visualized_images = True
    frames_to_plot = [0]
    low_res_img_to_plot = [0, 1, 2]
    db_range = 50

    # Reconstruct the image and visualize
    beamformer_cartesian(path_to_dataset,
                         decimation_factor,
                         interpolation_factor,
                         img_res,
                         image_x_range,
                         image_z_range,
                         save_images_to_hdf5=save_images_to_hdf5,
                         save_lri_to_hdf5=save_lri_to_hdf5,
                         save_visualized_images=save_visualized_images,
                         save_path=up(abspath(__file__)),
                         frames_to_plot=frames_to_plot,
                         low_res_img_to_plot=low_res_img_to_plot,
                         db_range=db_range,
                         alpha_fov_apod=alpha_fov_apod,
                         active_elements=active_elements,
                         frames_to_process=frames_to_process,
                         acqs_to_process=acqs_to_process)