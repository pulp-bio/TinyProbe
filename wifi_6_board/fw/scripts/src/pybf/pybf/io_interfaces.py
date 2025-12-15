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

import h5py
import numpy as np

from .transducer import Transducer
from .hardware import Hardware


class DataLoader:
    def __init__(self, path_to_dataset):
        # Load hdf5 dataset
        self._file = h5py.File(path_to_dataset, "r")

        # Calculate number of frames
        self._num_of_frames = len(list(self._file["data/rf_data"].keys()))

        # Calculate number of acquisitions per frame
        self._num_of_acq_per_frame = len(
            list(self._file["data/rf_data/frame_1"].keys())
        )

        # Get real sampling of the data
        self._f_sampling = self._file["data/f_sampling"][()].item()

        # Get frames per second
        self._fps = self._file["data/fps"][()].item()

        # Check the type of the dataset: experimental or simulation
        # If sim_params group is empty then it is experimental data
        if "sim_params" in list(self._file.keys()):
            self._simulation_flag = True
        else:
            self._simulation_flag = False

        # Create Transducer object
        self._create_transducer_obj()

        # Create USHardware object
        self._create_hardware_obj()

        return

    def close_file(self):
        self._file.close()

    def _create_transducer_obj(self):
        # Calculate bandwidth separately
        bw_hz = (
            self._file["trans_params/bandwidth"][()]
            * self._file["trans_params/f_central"][()].item()
        )

        self._transducer = Transducer(
            num_of_x_elements=self._file["trans_params/x_num_of_elements"][()].item(),
            num_of_y_elements=self._file["trans_params/y_num_of_elements"][()].item(),
            x_pitch=self._file["trans_params/x_pitch"][()].item(),
            y_pitch=self._file["trans_params/y_pitch"][()].item(),
            x_width=self._file["trans_params/x_width"][()].item(),
            y_width=self._file["trans_params/y_width"][()].item(),
            f_central_hz=self._file["trans_params/f_central"][()].item(),
            bandwidth_hz=bw_hz,
        )

        return

    def _create_hardware_obj(self):
        if self._simulation_flag:
            str_temp = "sim_params/"

            self._hardware = Hardware(
                f_sampling_hz=self._file[str_temp + "f_sim_hz"][()].item(),
                excitation=self._file[str_temp + "excitation"][()],
                impulse_response=self._file[
                    str_temp + "electroacoustic_impulse_response"
                ][()],
                start_time_s=self._file[str_temp + "start_time"][()].item(),
            )

        else:
            str_temp = "hardware_params/"

            self._hardware = Hardware(
                f_sampling_hz=self._file[str_temp + "f_sampling_hz"][()].item(),
                start_time_s=self._file[str_temp + "start_time"][()].item(),
                correction_time_shift_s=self._file[str_temp + "correction_time"][
                    ()
                ].item(),
            )
        return

    # Get the RF data for the mth acquisition of nth frame
    def get_rf_data(self, n_frame, m_acq):
        if n_frame > self._num_of_frames:
            print("DataLoader: n_frame ", n_frame, " exceeds the range")
            print("DataLoader: total number of frames is ", self._num_of_frames)
            return None

        if m_acq > self._num_of_acq_per_frame:
            print("DataLoader: m_acq exceeds the range")
            return None

        # Create a path to shot (in rf dataset m_acq starts from 1 (due to Matlab),
        # but in Python first acquisition correcponds to shot_1)
        # The same works for Frame number
        shot_path = (
            "data/rf_data/" + "frame_" + str(n_frame + 1) + "/shot_" + str(m_acq + 1)
        )

        # Check if all elements of the transducer were active or not
        if self._transducer._active_elements is None:
            rf_data = self._file[shot_path][()]
        else:
            # Select some channels
            rf_data = self._file[shot_path][()][self.transducer._active_elements, :]

        return rf_data.astype(np.float32)

    # Get positions of the scatters
    def get_scatters_pos(self):
        if self._simulation_flag == True:
            return self._file["sim_params/scatters_data"][()]
        else:
            print(
                "DataLoaders: Scatters positions are available only in simulation mode."
            )
            return None

    # Get TX strategy
    @property
    def tx_strategy(self):
        temp_path = "data/tx_mode"

        # Get the TX strategy name
        tx_strat_str = list(self._file[temp_path].keys())[0]

        # Get the TX strategy params
        params = self._file[temp_path + "/" + tx_strat_str][()]

        return (tx_strat_str, params)

    # Returns number of frames
    @property
    def num_of_frames(self):
        return self._num_of_frames

    # Returns number of acquisitions per frame
    @property
    def num_of_acq_per_frame(self):
        return self._num_of_acq_per_frame

    # Returns real sampling rate of rf data
    @property
    def f_sampling(self):
        return self._f_sampling

    # Returns fps that defines time delay between frames
    @property
    def fps(self):
        return self._fps

    # Returns an instance of transducer object
    @property
    def transducer(self):
        return self._transducer

    # Returns an instance of hardware object
    @property
    def hardware(self):
        return self._hardware

    # Simulation flag
    @property
    def simulation_flag(self):
        return self._simulation_flag


# Class to save beamformed images
class ImageSaver:
    def __init__(self, path_to_dataset):
        # Read/write if exists, create otherwise (default)
        self._file = h5py.File(path_to_dataset, "w")
        self.close_file()

        self._file = h5py.File(path_to_dataset, "a")

        self.data_subgroup = self._file.create_group("beamformed_data")
        self.params_subgroup = self._file.create_group("params")
        return

    def close_file(self):
        self._file.close()

    # Save the image data in a dataset according to the format
    # imgs_data has shape (n_images x n_x_points x n_y_points)
    def save_low_res_images(self, imgs_data, frame_number, low_res_imgs_indices=None):
        name = "/beamformed_data/frame_" + str(frame_number)
        group = self._file.require_group(name)

        # save low resolution images
        # If the list of indices was provided then use it to name datasets
        if low_res_imgs_indices is None:
            low_res_imgs_indices = [i for i in range(imgs_data.shape[0])]
        else:
            if len(low_res_imgs_indices) != imgs_data.shape[0]:
                print(
                    "ImageSaver: len of indices list = ",
                    len(low_res_imgs_indices),
                    "is not equal to data shape =",
                    imgs_data.shape[0],
                )

        for m_shot in low_res_imgs_indices:
            dataset = group.create_dataset(
                "low_res_image_" + str(m_shot), data=imgs_data[m_shot, :]
            )
        return

    # Save the image data in a dataset according to the format
    # img_data has shape (n_x_points x n_y_points)
    def save_high_res_image(self, img_data, frame_number):
        name = "/beamformed_data/frame_" + str(frame_number)
        group = self._file.require_group(name)

        # save high resolution images
        dataset = group.create_dataset("high_res_image", data=img_data)
        return

    # Save the image params in a dataset according to the format
    def save_params(self, pixels_coords, image_size, elements_coords, fps):
        # Save pixels coords
        dataset = self.params_subgroup.create_dataset(
            "pixels_coords_x_z", pixels_coords.shape, data=pixels_coords
        )

        # Save image resolutions
        dataset = self.params_subgroup.create_dataset(
            "image_resolution", image_size.shape, data=image_size
        )

        # Save elements coords
        dataset = self.params_subgroup.create_dataset(
            "elements_coords", elements_coords.shape, data=elements_coords
        )

        # Save fps
        dataset = self.params_subgroup.create_dataset("fps", data=fps)
        return

    # Save the simulation params in a dataset according to the format
    def save_simulation_params(self, scatters_coords):
        # Create subgroup
        group = self._file.require_group("sim_params")

        # save pixels coords
        dataset = group.create_dataset(
            "scatters_data", scatters_coords.shape, data=scatters_coords
        )

        return


# Class to save beamformed images
class ImageLoader:
    def __init__(self, path_to_dataset):
        # Open for read
        self._file = h5py.File(path_to_dataset, "r")

        # Create data subgroup
        self._data_subgroup = self._file["/beamformed_data"]

        # Calculate number of frames
        frame_names_list = list(self._data_subgroup.keys())
        self._num_of_frames = len(frame_names_list)
        print("ImageLoader: number of available frames = ", self._num_of_frames)

        # Calculate indices of existing frames
        self._frames_indices = [
            int(filename.split("_")[-1]) for filename in frame_names_list
        ]

        # Calculate number of low resolution images per frame
        # Each folder containts low res images + 1 high resolution image
        lri_names_list = list(self._data_subgroup["frame_0"].keys())

        # Kick out high resolution image
        if "high_res_image" in lri_names_list:
            lri_names_list.remove("high_res_image")

        self._num_of_low_res_img_per_frame = len(lri_names_list)

        # Calculate indices of existing low resolution images
        self._lri_indices = [
            int(filename.split("_")[-1]) for filename in lri_names_list
        ]
        print(
            "ImageLoader: number of available LRIs per frame = ",
            self._num_of_low_res_img_per_frame,
        )
        print("ImageLoader: Indices of available LRIs = ", self._lri_indices)

        # Check the type of the dataset: experimental or simulation
        # If sim_params group is empty then it is experimental data
        if "sim_params" in list(self._file.keys()):
            self._simulation_flag = True
        else:
            self._simulation_flag = False

        return

    def close_file(self):
        self._file.close()

    # Get the Image data for the mth acquisition of nth frame
    def get_low_res_image(self, n_frame, m_low_res_img):
        if n_frame not in self._frames_indices:
            print(
                "ImageLoader: n_frame = ", n_frame, " is not available in the dataset"
            )
            return None

        if m_low_res_img not in self._lri_indices:
            print(
                "ImageLoader: m_low_res_img = ",
                m_low_res_img,
                " is not available in the dataset",
            )
            return None

        # Create a path to the image
        img_path = "frame_" + str(n_frame) + "/low_res_image_" + str(m_low_res_img)

        return self._data_subgroup[img_path][()]

    # Get the high resolution image
    def get_high_res_image(self, n_frame):
        if n_frame not in self._frames_indices:
            print(
                "ImageLoader: n_frame = ", n_frame, " is not available in the dataset"
            )
            return None

        # Create a path to the image
        img_path = "frame_" + str(n_frame) + "/high_res_image"

        return self._data_subgroup[img_path][()]

    # Get positions of the scatters
    def get_scatters_coords(self):
        if self._simulation_flag == True:
            return self._file["sim_params/scatters_data"][()]
        else:
            print(
                "ImageLoader: Scatters positions are available only in simulation mode."
            )
            return None

    # Get pixels coords
    def get_pixels_coords(self):
        return self._file["params/pixels_coords_x_z"][()]

    # Get elements coords
    def get_elements_coords(self):
        return self._file["params/elements_coords"][()]

    # Get elements coords
    def get_fps(self):
        return self._file["params/fps"][()]

    # Returns a list of found frames
    @property
    def frame_indices(self):
        return self._frames_indices

    # Returns a list of found low resolution images
    # for a single frame
    @property
    def lri_indices(self):
        return self._lri_indices
