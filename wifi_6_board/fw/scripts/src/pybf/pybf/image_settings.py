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

class ImageSettings:
    def __init__(self,  
                 image_size_x_0,
                 image_size_x_1,
                 image_size_z_0,
                 image_size_z_1,
                 lateral_pixel_density,
                 transducer_obj):

        # Copy transducers params
        self._transducer = transducer_obj

        # Copy image params
        self._image_size_x_0 = image_size_x_0
        self._image_size_z_0 = image_size_z_0
        self._image_size_x_1 = image_size_x_1
        self._image_size_z_1 = image_size_z_1

        self._image_size_x = abs(image_size_x_1 - image_size_x_0)
        self._image_size_z = abs(image_size_z_1 - image_size_z_0)

        # Number of pixels per distance between transducers
        self._lat_pixel_density = lateral_pixel_density

        self._calc_min_axial_resolution()

        # Calculate high resolution for images
        self._calc_high_res()

        return

    def _calc_min_axial_resolution(self):

        self._axial_res_min = 1 / self._transducer.bandwidth_hz * self._transducer.speed_of_sound
        return

    def _calc_high_res(self):

        # Calculate number of x pixels
        n_x = np.round(self._image_size_x / self._transducer._x_pitch * self._lat_pixel_density)
        n_x = n_x.astype(int).item()

        # Calculate number of z pixels
        n_z = np.round(self._image_size_z / self._axial_res_min)
        n_z = n_z.astype(int).item()

        self._high_resolution = (n_x, n_z)

        return self._high_resolution


    def get_pixels_coords(self, x_res=None, z_res=None):
        
        if x_res is not None:
            n_x = x_res
        else:
            n_x = self._high_resolution[0]

        if z_res is not None:
            n_z = z_res
        else:
            n_z = self._high_resolution[1]

        # Calculate positions
        x_coords = np.linspace(self._image_size_x_0, self._image_size_x_1, n_x)
        x_coords = x_coords.reshape(-1,)

        # Calculate positions
        z_coords = np.linspace(self._image_size_z_0, self._image_size_z_1, n_z)
        z_coords = z_coords.reshape(-1,)

        self._pixels_coords = np.transpose(np.dstack(np.meshgrid(x_coords, z_coords)).reshape(-1, 2))

        return self._pixels_coords
    
    def get_max_resolution(self):
        return self._high_resolution