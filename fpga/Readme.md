# TinyProbe FPGA project
This repository contains Microsemi Libero FPGA project for TinyProbe wearable ultrasound system
## Structure of the project
- sources - source RTL files
- project - Libero project folder

## How to clone the repository and open the project
1. To clone the main repository with all submodules execute the following command in the terminal: <br /> 
`git clone --recurse-submodules git@iis-git.ee.ethz.ch:vsergei/tiny_probe_fpga_project.git`
2. After cloning create environmental variable **TINY_PROBE_SRC_PATH** pointing to `root_folder/sources` folder of the repository.
3. Open the project file `root_folder/project/tiny_probe.prjx` in Libero SoC.

### Usefull commands to work with git submodules:
- `git submodule update --init --recursive` - To pull down all submodules locally
- `git submodule update --recursive --remote` - To update submodules

 
### Requirements:
1. Windows Machine
2. Libero SoC v12.6