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

from pybf.scripts.make_video import make_video

if __name__ == '__main__':

    # Following dataset released under CC BY license (see data/README.md for details) 
    dataset_file_path = path_to_lib + '/pybf/tests/data/image_dataset.hdf5'

    db_range = 50
    video_fps = 30

    # Make video
    make_video(dataset_file_path,
               db_range=db_range,
               video_fps=video_fps,
               save_path=up(abspath(__file__)))