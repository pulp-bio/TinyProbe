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
import argparse
import numpy as np
import sys
from os.path import dirname, abspath

from ..pybf.io_interfaces import ImageLoader
from ..pybf.visualization import plot_image


def visualize_image_dataset(
    path_to_img_dataset,
    save_path=None,
    save_visualized_images=False,
    show_images=True,
    frames_to_plot=None,
    low_res_img_to_plot=None,
    db_range=None,
):
    # Load beamformed images
    imgLoader = ImageLoader(path_to_img_dataset)

    # Check path to save images
    if save_path is None:
        # Construct save path (save to dataset folder)
        len_to_cut = len(path_to_img_dataset.split("/")[-1])
        save_path = path_to_img_dataset[: -1 - len_to_cut]

    # Check simulation flag
    if imgLoader._simulation_flag:
        scs_coords_xz = imgLoader.get_scatters_coords()[[0, 1], :]
    else:
        scs_coords_xz = None

    # Get the coordinates of transducer elements
    elements_coord = imgLoader.get_elements_coords()

    # Calculate image sizes
    pixels_coords = imgLoader.get_pixels_coords()
    image_size_x_0 = pixels_coords[0, :].min()
    image_size_x_1 = pixels_coords[0, :].max()
    image_size_z_0 = pixels_coords[1, :].min()
    image_size_z_1 = pixels_coords[1, :].max()

    # Check the frames_to_plot list
    if frames_to_plot is not None:
        if len(frames_to_plot) == 0:
            frames_to_plot = imgLoader.frame_indices
    else:
        frames_to_plot = []

    # Check the low_res_img_to_plot list
    if low_res_img_to_plot is not None:
        if len(low_res_img_to_plot) == 0:
            low_res_img_to_plot = imgLoader.lri_indices
    else:
        low_res_img_to_plot = []

    # Iterate over frames amd low resolution images
    for n_frame in frames_to_plot:
        # Plot Low Resolution Images
        for n_lri in low_res_img_to_plot:
            # Get data
            img_data = imgLoader.get_low_res_image(n_frame, n_lri)
            # Extract envelope
            img_data = np.abs(img_data)

            plot_image(
                img_data,
                elements_coords_xz=elements_coord,
                title="Frame " + str(n_frame) + " LRI " + str(n_lri),
                image_x_range=[image_size_x_0, image_size_x_1],
                image_z_range=[image_size_z_0, image_size_z_1],
                db_range=db_range,
                scatters_coords_xz=scs_coords_xz,
                framework="plotly",
                save_fig=save_visualized_images,
                show=show_images,
                path_to_save=save_path,
            )

        # Plot High Resolution Image
        # Get data
        img_data = imgLoader.get_high_res_image(n_frame)
        # Extract envelope
        img_data = np.abs(img_data)
        plot_image(
            img_data,
            elements_coords_xz=elements_coord,
            title="Frame " + str(n_frame) + " HRI",
            image_x_range=[image_size_x_0, image_size_x_1],
            image_z_range=[image_size_z_0, image_size_z_1],
            db_range=db_range,
            scatters_coords_xz=scs_coords_xz,
            framework="plotly",
            save_fig=save_visualized_images,
            show=show_images,
            path_to_save=save_path,
        )

    # Close the file with beamformed images
    imgLoader.close_file()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path_to_img_dataset",
        type=str,
        default="",
        help="Path to the image dataset file.",
    )

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "True", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "False", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    # Parameters for visualization
    parser.add_argument(
        "--save_visualized_images",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Flag to save visualized images.",
    )
    parser.add_argument(
        "--frames_to_plot",
        type=int,
        nargs="+",
        default=None,
        help='Space separated list of frames to plot.\
        "[]" - plot all frames. "None" - plot none.',
    )
    parser.add_argument(
        "--low_res_img_to_plot",
        type=int,
        nargs="+",
        default=None,
        help='Space separated list of low resolution images to plot.\
        "[]" - plot all frames. "None" - plot none.',
    )
    parser.add_argument(
        "--db_range",
        type=float,
        default=None,
        help="Decibels range for log compression of images ",
    )

    FLAGS, unparsed = parser.parse_known_args()

    # Run main function
    visualize_image_dataset(
        FLAGS.path_to_img_dataset,
        FLAGS.save_visualized_images,
        FLAGS.frames_to_plot,
        FLAGS.low_res_img_to_plot,
        FLAGS.db_range,
    )
