"""
   Copyright (C) 2021 ETH Zurich. All rights reserved.

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
import numpy as np
import sys

# Insert path to pybf library to system path
path_to_lib = up(up(up(up(up(abspath(__file__))))))
sys.path.insert(0, path_to_lib)

from pybf.scripts.beamformer_cartesian_realtime import BFCartesianRealTime
from pybf.pybf.transducer import Transducer
from pybf.pybf.image_settings import ImageSettings
from pybf.pybf.visualization import plot_image

if __name__ == '__main__':

    # Following dataset released under CC BY license (see data/README.md for details) 
    path_to_dataset = path_to_lib + '/pybf/tests/data/sample_rf_data.csv'
    rf_data = np.genfromtxt(path_to_dataset, delimiter=',')

    ### Specify Trancducer settings and create transducer object ###

    # Transucer sttings
    F_CENTRAL = 5.2083 * 10 ** 6
    c = 12 * 10 ** 6
    X_ELEM = 192
    X_PITCH = 0.0003
    X_WIDTH = 0
    Y_ELEM = 1
    Y_PITCH = 0
    Y_WIDTH = 0

    trans = Transducer(num_of_x_elements=X_ELEM,
                       num_of_y_elements=Y_ELEM,
                       x_pitch=X_PITCH,
                       y_pitch=Y_PITCH,
                       x_width=X_WIDTH,
                       y_width=Y_WIDTH,
                       f_central_hz=F_CENTRAL,
                       bandwidth_hz=F_CENTRAL,
                       active_elements=None)

    ### Specify Image settings and create corresponding object ###

    img_res = [400, 600]
    image_x_range = [-0.022, 0.022]
    image_z_range = [0.0014784, 0.04]

    db_range = 40

    LATERAL_PIXEL_DENSITY_DEFAULT = 5

    img_config = ImageSettings(image_x_range[0],
                               image_x_range[1],
                               image_z_range[0],
                               image_z_range[1],
                               LATERAL_PIXEL_DENSITY_DEFAULT,
                               trans)

    ### Specify preprocessing parameters for RF data ###

    decimation_factor = 1
    interpolation_factor = 10

    ### Specify TX strategy and Apodization parameters ###

    start_time = -1.0666666666666665e-06
    correction_time_shift = 2.6e-06

    alpha_fov_apod = 40

    # 1 Plane waves with inclination angle 0
    tx_strategy = ['PW_1_0', [0]]

    ### Specify Sampling Frequency ###

    SAMPLING_FREQ = 20 * 10 ** 6 

    bf = BFCartesianRealTime(SAMPLING_FREQ,
                             tx_strategy,
                             trans,
                             decimation_factor,
                             interpolation_factor,
                             img_res,
                             img_config,
                             start_time=start_time,
                             correction_time_shift=correction_time_shift,
                             alpha_fov_apod=alpha_fov_apod,
                             bp_filter_params=None)

    # Run beamformer
    img_data = bf.beamform(rf_data)

    # Plot image and save it.
    plot_image(np.abs(img_data), 
               scatters_coords_xz=None,
               elements_coords_xz=None,
               framework='plotly',
               title='Sample Image',
               image_x_range=image_x_range,
               image_z_range=image_z_range,
               db_range=50,
               colorscale='Greys',
               save_fig=True, 
               show=False,
               path_to_save='.')



