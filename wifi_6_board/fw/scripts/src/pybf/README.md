# PyBF: Python Ultrasound Beamformer

# Introduction

This repository contains the work in progress on a Python Ultrasound Beamformer Library (PyBF).

It contains:
- input/output utilities to load raw RF data from a dataset and save reconstructed images (enabled by **h5py** package),
- RF signal processing functions (enabled by **scipy**),
- delay and sum beamformer (implemented either with **numpy** or plain Python + **numba**),
- Two different Minimum Variance Beamformers (**numpy** only iplementation),
- visualization utilities (enabled by **matplotlib** and **plotly** libraries)

# Structure of the repository

This repository contains:

- `pybf` folder contains the source code with low-level routines.
 
- `scripts` folder contains high-level functions such as `beamformer_cartesian.py` that implements entire pipeline for image reconstruction and a collection of functions to quantitatively evaluate US-images by FWHM and CNR

- `tests` folder contains 
    - simple tests for the library (located in `code` directory):
        - `realtime_beamformer` demonstrates the cartesian dynamic receive beamformer that inputs simulated RF data captured with a single plane wave modality, reconstructs and then visualizes the image of the virtual scatters. The example demonstrates the usage of `BFCartesianRealTime` class which can be easily integrated into the 3rd party python scripts for continuous image reconstruction.
        - `plane_wave_3_test` demonstrates the cartesian dynamic receive beamformer that inputs simulated RF data captured with plane wave modality (3 plane waves), reconstructs and then visualizes the images of the virtual scatters. The script operates with hdf5 data format (see )
        - `low_ch_das_vs_mvbf_spatial` compares the performance of the conventional delay-and-sum (DAS) beamformer with 
        minimum variance beamformer with spatial smoothing (MVBFspatial or MVBFss) on PICMUS dataset (see `.data/README.md` for details) [1,2].
        - `low_ch_mvbf_global` demonstrates the MVBF global beamformer. (not a practical beamformer but interesting for instructional purposes)
        - `low_ch_mvbf_jupyter` contains interactive Jupyter notebook comparing the referenmce DAS beamformer with Data-Compounded-on-Receive (DCR-MVDR) beamformer.[3,4]
        - `make_video` demonstrates how to produce a video from a reconstructed image dataset.
    - sample datasets required for the tests (located in `data` directory) + brief description of the datasets' internal structure. The PICMUS dataset required by some of the above tests should be downloaded  from [here](https://polybox.ethz.ch/index.php/s/OVgmRABIpHIvaJ9) and copied to the `tests/data`. 

# Installation and usage

To install the library we advise using [miniconda](https://docs.conda.io/en/latest/miniconda.html) package manager and create a virtual environment.
To do it:
1. Download the repository to your local PC 
2. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html)
3. Add additional channels for necessary packages by executing the following commands in terminal
```bash
conda config --append channels plotly
conda config --append channels conda-forge
```
4. Move to the library directory
5. Execute the command below to create a virtual environment named `pybf_env` and install all necessary libraries listed in `requirements.txt`
```bash
conda create --name pybf_env python=3.6 --file requirements.txt
```
**Note:** If you have problems with installing the packages you can do it manually.  Critical packages for the library are:
- numpy
- matplotlib
- scipy
- h5py
- plotly
- plotly-orca
- psutil
- requests
- opencv
- numba

The docs for the library and additional functionality will come later. To use existing features we advise exploring the provided tests.

To run the test: 
1. Run a terminal and activate conda environment
```bash
conda activate pybf_env
```
2. Navigate to the directory of the test
3. Execute 
```
python main.py
```

# Quick-Start - Beamformer Comparison

All code necessary to acquaint oneself with the *pybf* library's different beamformers is located under `tests/code/`. For example, the two Jupyter notebooks (or the interactive python script) under `tests/code/low_ch_mvbf_jupyter` provide the whole image creation pipeline including the quantitative image evaluation steps. The notebooks contain a full setup to compare two beamformer classes of choice and corresponding explanations of some important code parameters.

All beamformer classes generally share the same output interface and a basic set of common input interfaces. The `BFMVBFspatial` (a FB-SS-MVBF) has an extra attribute `window_width` that defines the sub-aperture's size. For proper performance it is advised to keep it below half the number of channels. Furthermore, this beamformer becomes very compuationally expensive when using a high sub-aperture size. (Consider that a 128-ch setup with a sub-aperture of 64 will require 400x600=240.000 inversions of a 64x64 matrix witht the standard image quality.) The `BFMVBFdcr` (a DCR-MVBF) has an extra attribute `is_approx_inv`

# Works that use PyBF
- Leitner, C., Vostrikov, S., Penasso, H., Hager, P. A., Cossettini, A., Benini, L., & Baumgartner, C. (2020, July). Fascicle Contractility in Deep and Pennate Skeletal Muscle Structures: A Method to Detect Motor Endplate Bands In-Vivo using Ultrafast Ultrasound. In Proceedings of the 2020 IEEE International Ultrasonics Symposium (IUS). IEEE Xplore.
- Leitner, C., Vostrikov, S., Penasso, H., Hager, P. A., Cosscttini, A., Benini, L., & Baumgartner, C. (2020, September). Detection of Motor Endplates in Deep and Pennate Skeletal Muscles in-vivo using Ultrafast Ultrasound. In 2020 IEEE International Ultrasonics Symposium (IUS) (pp. 1-7). IEEE.
# References

[1] - M. Sasso and C. Cohen-Bacrie, “Medical ultrasound imaging using the fully adaptive
beamformer,” in Proceedings. (ICASSP ’05). IEEE International Conference on
Acoustics, Speech, and Signal Processing, 2005.

[2] - B. M. Asl and A. Mahloojifar, “Contrast enhancement and robustness improvement
of adaptive ultrasound imaging using forward-backward minimum variance
beamforming” IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control

[3] - G. Montaldo, M. Tanter, J. Bercoff, N. Benech, and M. Fink, “Coherent plane-wave
compounding for very high frame rate ultrasonography and transient elastography”
IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control

[4] - M.K. Son, N. Sim, T.Chiueh, "A Novel Minimum Variance Beamformer and Its Circuit Design for Ultrasound Beamforming"
2020 International Symposium on VLSI Design, Automation and Test (VLSI-DAT)

# License
All source code is released under Apache v2.0 license unless noted otherwise, please refer to the LICENSE file for details.
Example datasets under `tests/data` provided under a [Creative Commons Attribution 4.0 International License][cc-by] 

[cc-by]: http://creativecommons.org/licenses/by/4.0/
