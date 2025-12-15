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

# Calculate propagation delays from the transducer to the pixel point and back
def calc_propagation_delays(tx_strategy, 
                            num_of_elements, 
                            elements_coords, 
                            pixels_coords, 
                            speed_of_sound,
                            simulation_flag = False,
                            do_print = False,
                            ):

    # Calculate the number of channels for given data
    num_of_elements = elements_coords.shape[1]

    # Check the dimensions
    # The script can calculate the delays in both 2D and 3D
    # The input parameters should be aligned in dimensions
    if (elements_coords.shape[0] != pixels_coords.shape[0]):
        print('Error: Transducer element coordinates and pixel coordinates have different dimensions')
        return

    # Parametrised name of TX strategy
    # E.g. 'PW_3_12'
    tx_strat_name = tx_strategy[0].split('_')
    # Parameters of TX strategy
    tx_strat_params = tx_strategy[1]

    if tx_strat_name[0] == 'PW':

        num_of_pw = int(tx_strat_name[1])
        max_angle = float(tx_strat_name[2])

        # Print info
        if do_print:
            print('TX strategy: plane waves')
            print('Number of plane waves: ', num_of_pw)
            print('Maximum angle: ', max_angle, '°')

        # Calculate angles
        pw_angles_rad = np.radians(np.linspace(-max_angle, max_angle, num_of_pw))
        pw_angles_rad = pw_angles_rad.reshape(-1, 1)

    
        # Calculate delays from pw lines to points 
        # In simulation plane wave front crosses x=0 line in a point x_0 = 0
        # So the delays for the pixels points in the area of observation can be negative
        # In real systems plane wave the delays should be positive
        if simulation_flag:
            elements_coords_x_max = 0
        else:
            elements_coords_x_max = np.amax(elements_coords[0,:])

        # Output: (n_angles x n_points)
        tx_delays = calc_dist_from_pw_line_to_point_2(pw_angles_rad,
                                                      pixels_coords,
                                                      elements_coords_x_max)
        tx_delays = tx_delays / speed_of_sound

        # Calculate delays from points to elements
        # Output: distance (n_elements x n_points)  
        rx_delays = calc_dist_from_point_to_element(elements_coords, 
                                                    pixels_coords)
                                    
        rx_delays = rx_delays / speed_of_sound

        n_angles = tx_delays.shape[0]
        n_points = tx_delays.shape[1]
        n_elements = rx_delays.shape[0]

        # delays = np.zeros((n_angles, n_elements, n_points))

        # # Combine two delays together
        # # 1 Expand rx_delays array, adding 3rd dimension (of size n_angles)
        # # 2 Reshape tx_delays and sum it with expanded rx_delays array
        # delays = np.tile(rx_delays, (n_angles, 1, 1))
        # delays = delays + tx_delays.reshape(n_angles, 1, n_points)


    # Output shape of delays
    # rx_delays: (n_elements x n_points)
    # tx_delays: (n_angles x n_points)
    return rx_delays.astype(np.float32), tx_delays.astype(np.float32)

# Calculates distance from point to plane wave front
# Function is vectorized. 
# Input: pw_angles of size (n_angles X 1)
# point_coord_x_z of size (2 x n_points)
# Output: (n_angles x n_points)

# NOTE: This function is more general than 
# calc_dist_from_pw_line_to_point_2 but there is an error in angle's signs
# TBD: find a bug with angle signs
def calc_dist_from_pw_line_to_point(pw_angle, point_coord_x_z, max_x_coord):

    # An equation of line on a xz plane is ax + bxz + c = 0
    # An equation for PW is z = (x + sgn(-alpha) * xl/2) * tg(-alpha)
    # where xl/2 - half length of the transducer array, alpha - tilting angle 
    # Then a = tg(-alpha)
    # b = -1
    # c = xl/2 * sgn(-alpha) * tg(-alpha)

    a = np.tan(-pw_angle.reshape(-1, 1))
    b = -1
    c = max_x_coord * np.multiply(np.sign(pw_angle.reshape(-1, 1)), a)

    x_coord = point_coord_x_z[0,:].reshape(1, -1)
    z_coord = point_coord_x_z[1,:].reshape(1, -1)

    # Calculate distance (https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line)
    distance = np.absolute(np.matmul(a, x_coord) + b * z_coord + c)
    denominator = np.sqrt(np.sum(np.square(a) + np.square(b), axis=1, keepdims=True))
    distance = np.divide(distance, denominator)

    return distance

# Calculates distance from point to plane wave front
# based on the formula from paper 
# "Wireless_Real-Time_Plane-Wave_Coherent_Compounding_on_an_iPhone_A_Feasibility_Study"
# Function is vectorized. 
# Input: pw_angles of size (n_angles X 1)
# point_coord_x_z of size (2 x n_points)
# Output: (n_angles x n_points)
def calc_dist_from_pw_line_to_point_2(pw_angle, point_coord_x_z, max_x_coord):

    # Distance equalss z * cos(alpha) + (x_0 - x) * sin(alpha)

    # pw_angles_local = pw_angle.reshape(-1, 1)
    # TBD Hot fix for angle direction
    pw_angles_local = -pw_angle.reshape(-1, 1)

    # Coordinate where pw line crosses x axis
    x_0 = np.sign(pw_angles_local.reshape(-1, 1)) * max_x_coord

    x_coords = point_coord_x_z[0,:].reshape(1, -1)
    z_coords = point_coord_x_z[1,:].reshape(1, -1)

    # Calculate distance 
    # ("Wireless_Real-Time_Plane-Wave_Coherent_Compounding_on_an_iPhone_A_Feasibility_Study")
    distance = np.multiply(z_coords, np.cos(pw_angles_local)) + np.multiply((x_0 - x_coords), np.sin(pw_angles_local))

    return distance

# Calculate distance from point to element
# Input:  points_coords (n_dim x n_points)
# elements_coords (n_dim x n_points)
# Output: distance (n_elements x n_points)
def calc_dist_from_point_to_element(elements_coords, points_coords):

    n_elements = elements_coords.shape[1]
    n_points = points_coords.shape[1]
    n_dim = points_coords.shape[0]

    # Allocate memory
    distance = np.zeros((n_elements, n_points))

    # 1 Expand points_coord array, adding 3rd dimension
    # 2 Substract elements_coord
    # 3 Calculate the distance using L2 norm
    distance = np.tile(points_coords,(n_elements, 1, 1))
    distance = distance - np.transpose(elements_coords).reshape(n_elements, n_dim, 1)
    distance = np.linalg.norm(distance, ord=2, axis=1)

    return distance

def convert_time_to_samples(array_t, f_sampling, start_offset_s, correction_time_s):

    # 1 Substract start offset
    # 2 Sum correction time
    # 3 Multiply by sampling rate
    array_samples = np.rint(np.multiply(array_t - start_offset_s + correction_time_s, f_sampling))

    return array_samples.astype(np.int32)

