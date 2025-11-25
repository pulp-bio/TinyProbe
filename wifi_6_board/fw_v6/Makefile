PROJECT_NAME := fw_v6
CMAKE_DIR := cmake_gcc

PYTHON ?= python
COMMANDER ?= "C:/Users/cedr0/.silabs/slt/installs/archive/Simplicity Commander/commander.exe"

build: $(CMAKE_DIR)/build
	cmake --build cmake_gcc/build

configure: $(CMAKE_DIR)/build

$(CMAKE_DIR)/build: user/env.h
	cd $(CMAKE_DIR) && cmake -B build --preset project

flash: build
	$(COMMANDER) flash cmake_gcc/build/base/fw_v6.hex --device SIWG917

attach:
	sleep 1.5
	$(COMMANDER) rtt connect --device SIWG917

user/env.h: .env
	$(PYTHON) scripts/fetch_env.py $< $@

clean:
	rm -rf $(CMAKE_DIR)/build user/env.h

.PHONY: build configure flash attach clean