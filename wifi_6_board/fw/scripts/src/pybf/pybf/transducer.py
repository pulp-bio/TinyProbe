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

SPEED_OF_SOUND = 1540  # meters per second


class Transducer:
    def __init__(
        self,
        num_of_x_elements=1,
        num_of_y_elements=1,
        x_pitch: float = 0,
        y_pitch: float = 0,
        x_width: float = 0,
        y_width: float = 0,
        f_central_hz: float = 0,
        bandwidth_hz: float = 0,
        active_elements=None,
    ):
        self._num_of_x_elements = num_of_x_elements
        self._num_of_y_elements = num_of_y_elements
        self._num_of_elements = num_of_y_elements * num_of_x_elements

        self._x_pitch = x_pitch
        self._y_pitch = y_pitch

        self._x_width = x_width
        self._y_width = y_width

        self._f_central_hz = f_central_hz
        self._bandwidth_hz = bandwidth_hz

        self._speed_of_sound = SPEED_OF_SOUND

        # Calculate X, Y coordinates of transducer elements
        self._calc_elements_coords()

        # Check if active elements were specified
        # By default all the elements are active
        if active_elements is not None:
            self.set_active_elements(active_elements)
        else:
            self._active_elements = None

        return

    # Returns x,y coords for the elements of transducer
    def _calc_elements_coords(self):
        # Calc x coords
        x_coords = np.arange(0, self._num_of_x_elements) * (self._x_pitch)
        x_coords = x_coords.reshape(
            -1,
        )
        # Put zero to the center of array
        x_coords = x_coords - (x_coords[-1] - x_coords[0]) / 2

        # Cals y coords
        y_coords = np.arange(0, self._num_of_y_elements) * (self._y_pitch)
        y_coords = y_coords.reshape(
            -1,
        )
        # Put zero to the center of array
        y_coords = y_coords - (y_coords[-1] - y_coords[0]) / 2

        self._elements_coords = np.transpose(
            np.dstack(np.meshgrid(x_coords, y_coords)).reshape(-1, 2)
        )

        return

    # Set the active elements of the transducer by list of indices
    # Attention: elements numeration starts from 0
    def set_active_elements(self, active_elements, do_print=False):
        self._active_elements = np.array(active_elements, dtype=int)

        if do_print:
            print("Transducer: number of active elements = ", len(active_elements))

        # Calculate X, Y coordinates of transducer elements
        self._calc_elements_coords()

        # Update number of elements
        self._num_of_elements = len(self._active_elements)

        # Update coordinates of activated elements
        self._elements_coords = self._elements_coords[:, self._active_elements]

        return

    # Returns transducers elements coordinates
    @property
    def elements_coords(self):
        return self._elements_coords

    # Returns number of transducers elements
    @property
    def num_of_elements(self):
        return self._num_of_elements

    # Returns indices of active transducer elements
    @property
    def active_elements(self):
        return self._active_elements

    # Returns central frequency
    @property
    def f_central_hz(self):
        return self._f_central_hz

    # Returns bandwidth
    @property
    def bandwidth_hz(self):
        return self._bandwidth_hz

    # Returns speed of sound
    @property
    def speed_of_sound(self):
        return self._speed_of_sound
