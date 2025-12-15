## Test datasets 

# Introduction

Provided datasets `./rf_dataset.hdf5` and `./image_dataset.hdf5` contain **raw RF data** and **reconstructed image** required to run `plane_wave_3_test`and `make_video` tests respectively.

`./rf_dataset.hdf5` contains raw RF data obtained by ultrasound simulation of virtual scatters. The simulation was done using Field II program [[1-2]](#1).

`./image_dataset.hdf5` contains a single image reconstructed from `./rf_dataset.hdf5`  by cartesian dynamic receive beamformer (`beamformer_cartesian.py`).

Along with the data mentioned above the datasets include additional information required for data processing. The detailed description can be found below.

Moreover, we provide sample raw data array stored in `./sample_rf_data.csv`. This data is required to run the test `realtime_beamformer`.

The datasets under  `./Picmus` folder contain **raw RF data** from PICMUS challenge [[3]](#3). It is required to run `low_ch_*` tests.

# Structure of the datasets

There are two types of datasets which PyBF library is using:
1. RF datasets (e.g. `rf_dataset.hdf5`)
2. Image datasets (e.g `image_dataset.hdf5`)

Both of them use [hdf5](https://support.hdfgroup.org/HDF5/doc/H5.intro.html) hierarchical data format.

## For RF datasets the following groups and hdf5 datasets must be filled:
| **Dataset/group**                               | **Description**                                               |
| ------------------------------------------------|:--------------------------------------------------------------|
| data/rf_data/frame_**_l_**/shot_**_m_**         | RF data for **_m_** shot of **_l_** frame                     |
| data/f_sampling                                 | Sampling frequency in Hz for RF data                          |
| data/tx_mode                                    | Transmission mode that defines imaging modality               |
| data/fps                                        | Frame per second rate at which <br> the frames were captured  |
| trans_params                                    | Group that contains transducer <br >parameters                |
| trans_params/bandwidth                          | Transducer's banwidth in Hz <br> divided by central frequency |
| trans_params/f_central                          | Central frequency of the transducer in Hz                     |
| trans_params/x_num_of_elements                  | Number of transducer elements along x axis                    |
| trans_params/y_num_of_elements                  | Number of transducer elements along y axis                    |
| trans_params/x_pitch                            | X pitch of transducer elements                                |
| trans_params/y_pitch                            | Y pitch of transducer elements                                |
| trans_params/x_width                            | X width of a single transducer element                        |
| trans_params/y_width                            | Y width of a single transducer element                        |
| **_Only for simulation_**                                                                                       |
| sim_params                                      | Group that contains simualation parameters                    |
| sim_params/f_sim_hz                             | The frequency of data acquisition <br> during simulation      |
| sim_params/excitation                           | Transducer excitation function                                |
| sim_params/<br>electroacoustic_impulse_response | Spatial impulse response                                      |
| sim_params/start_time                           | The time of the first RF sample acquisition                   |
| sim_params/scatters_data                        | Spatial coordinates (x, y, z) <br> of virtual scatters        |
| **_Only for experimental data_**                                                                                |
| hardware_params                                 | Group that contains hardware <br >parameters                  |
| hardware_params/f_sampling_hz                   | The frequency of data acquisition <br> from hardware          |
| hardware_params/start_time                      | The time of the first RF sample acquisition                   |
| hardware_params/correction_time                 | The time shift caused by US pulse length                      |

## During the image reconstruction PyBF library creates the following groups and hdf5 datasets inside Image dataset file:
| **Dataset/group**                                         | **Description**                                              |
| ----------------------------------------------------------|:-------------------------------------------------------------|
| beamformed_data/frame_**_l_**/<br> low_res_image_**_m_**  | Reconstructed image for **_m_** shot of **_l_** frame        |
| beamformed_data/frame_**_l_**/<br> high_res_image         | Coherently compounded image for **_l_** frame                |
| params/pixels_coords_x_z                                  | Spatial coordinates (x, z) of image pixels                   |
| params/elements_coords                                    | Spatial coordinates (x, y, z) of transducer elements         |
| params/fps                                                | Frame per second rate at which <br> the frames were captured | 
| **_Only for simulation_**                                                                                                |
| sim_params                                                | Group that contains simualation parameters                   |
| sim_params/scatters_data                                  | Spatial coordinates (x, y, z) <br> of virtual scatters       |

# License
The datasets (`rf_dataset.hdf5` and `image_dataset.hdf5`) are licensed under a [Creative Commons Attribution 4.0 International
License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

# References
<a id="1">[1]</a> 
J.A. Jensen: Field: A Program for Simulating Ultrasound Systems, Paper presented at the 10th Nordic-Baltic Conference on Biomedical Imaging Published in Medical & Biological Engineering & Computing, pp. 351-353, Volume 34, Supplement 1, Part 1, 1996.

<a id="2">[2]</a> 
J.A. Jensen and N. B. Svendsen: Calculation of pressure fields from arbitrarily shaped, apodized, and excited ultrasound transducers, IEEE Trans. Ultrason., Ferroelec., Freq. Contr., 39, pp. 262-267, 1992.

<a id="3">[3]</a> 
Liebgott, Herve, et al. "Plane-wave imaging challenge in medical ultrasound." 2016 IEEE International ultrasonics symposium (IUS). IEEE, 2016.