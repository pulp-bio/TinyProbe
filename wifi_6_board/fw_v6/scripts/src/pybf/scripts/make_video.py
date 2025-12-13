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

import sys
from os.path import dirname, abspath
import cv2
import h5py
import numpy as np

from pybf.pybf.io_interfaces import ImageLoader
from pybf.pybf.visualization import log_compress


def make_video(dataset_file_path,
               db_range=50,
               video_fps=60,
               save_path=None):

    # Create image loader object
    image_loader = ImageLoader(dataset_file_path)

    # Get sorted list of available frame indices
    frames_list = image_loader.frame_indices
    frames_list.sort()

    # Get image shape in pixels
    img_shape = image_loader.get_high_res_image(frames_list[0]).shape

    # Get x and z ranges and define aspect ratio
    pixels_coords = image_loader.get_pixels_coords()
    x_range = pixels_coords[0,:].max() - pixels_coords[0,:].min()
    z_range = pixels_coords[1,:].max() - pixels_coords[1,:].min()
    aspect_ratio = x_range / z_range
    print("Aspect ratio: ", aspect_ratio)

    # Define output image shape
    img_shape_out = (img_shape[0], int(img_shape[0]/aspect_ratio))
    print("Output image resolution: ", img_shape_out)

    # Construct save path (save to dataset folder by default)
    if save_path is None:
        len_to_cut = len(dataset_file_path.split('/')[-1])
        save_path = dataset_file_path[:-1 - len_to_cut]

    video = cv2.VideoWriter(save_path + '/' + 'video.avi', cv2.VideoWriter_fourcc(*"MJPG"), int(video_fps), img_shape_out, 0)

    for n_frame in frames_list:
        # Take absolute value of high resilution frames
        frame_data = np.abs(image_loader.get_high_res_image(n_frame))

        # Make log compression
        frame_data_log = log_compress(frame_data, db_range)
        frame_data_log = frame_data_log + db_range

        # Convert to uint8_t
        frame_data_uint8 = np.uint8(frame_data_log/np.amax(frame_data_log) * 255)
        frame_final = cv2.resize(frame_data_uint8, img_shape_out)
        video.write(frame_final.astype('uint8'))
    
    # Close hdf5 file and video
    image_loader.close_file()
    video.release()

    return

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--dataset_file_path',
        type=str,
        default=' ',
        help='Path to the image dataset file.')
    parser.add_argument(
        '--db_range',
        type=float,
        default=50,
        help='Db range of images')
    parser.add_argument(
        '--video_fps',
        type=float,
        default=60,
        help='FPS of output video')

    FLAGS, unparsed = parser.parse_known_args()

    # Run main function
    make_video(FLAGS.dataset_file_path,
               db_range=FLAGS.db_range,
               video_fps=FLAGS.video_fps)