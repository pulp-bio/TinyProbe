PROJECT_NAME := fw
CMAKE_DIR := cmake_gcc

PYTHON ?= python
# Path to Simplicity Commander executable (adjust as needed)
COMMANDER ?= "C:/Users/cedr0/.silabs/slt/installs/archive/Simplicity Commander/commander.exe"

# Build the firmware with CMake/Ninja
build: $(CMAKE_DIR)/build
	cmake --build cmake_gcc/build

# Configure the project with CMake
configure: $(CMAKE_DIR)/build

# Configure the project with CMake
$(CMAKE_DIR)/build: user/env.h $(CMAKE_DIR)/.migrated
	cd $(CMAKE_DIR) && cmake -B build --preset project

# Run migration script to update CMake files
$(CMAKE_DIR)/.migrated: scripts/migrate.py
	$(PYTHON) scripts/migrate.py
	touch $@
	echo "Migration completed on $(shell date)" >> $@

# Flash the firmware to the device
flash: build
	$(COMMANDER) flash cmake_gcc/build/base/fw.hex --device SIWG917

# Attach to the device using RTT (without reset)
attach:
	sleep 1.5
	$(COMMANDER) rtt connect --device SIWG917 --speed 2500 --noreset

# Attach to the device using RTT (with reset)
attach_reset:
	$(COMMANDER) rtt connect --device SIWG917 --speed 2500

# Generate user/env.h from .env
user/env.h: .env
	$(PYTHON) scripts/fetch_env.py $< $@

# Clean build artifacts
clean:
	rm -rf $(CMAKE_DIR)/build user/env.h

# Build the docs using Doxygen
docs:
	cd docs && doxygen -q

.PHONY: build configure flash attach attach_reset clean docs $(CMAKE_DIR)/.migrated