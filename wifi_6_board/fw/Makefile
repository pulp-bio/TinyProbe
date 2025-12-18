PROJECT_NAME := fw_v6
CMAKE_DIR := cmake_gcc

PYTHON ?= python
# On Windows, the commander path is $(USERPROFILE)/.silabs/slt/installs/archive/Simplicity Commander/commander.exe
# On Linux/Mac, the commander path is $(HOME)/.silabs/slt/installs/archive/commander/commander
ifeq ($(COMMANDER),)
	ifeq ($(OS),Windows_NT)
		USER_HOME := $(subst \,/,$(USERPROFILE))
		COMMANDER := "$(USER_HOME)/.silabs/slt/installs/archive/Simplicity Commander/commander.exe"
	else
		COMMANDER := $(HOME)/.silabs/slt/installs/archive/commander/commander
	endif
endif

# Build the firmware with CMake/Ninja
build: $(CMAKE_DIR)/build
	cmake --build cmake_gcc/build

# Configure the project with CMake
configure: $(CMAKE_DIR)/build

# Configure the project with CMake
$(CMAKE_DIR)/build: user/env.h $(CMAKE_DIR)/.migrated
	cmake -E chdir $(CMAKE_DIR) cmake -B build --preset project

# Run migration script to update CMake files
$(CMAKE_DIR)/.migrated: scripts/migrate.py
	$(PYTHON) scripts/migrate.py
	touch $@
	echo "Migration completed on $(shell date)" >> $@

# Flash the firmware to the device
flash: build
	$(COMMANDER) flash cmake_gcc/build/base/$(PROJECT_NAME).hex --device SIWG917

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
	cmake -E rm -rf $(CMAKE_DIR)/build user/env.h $(CMAKE_DIR)/.migrated

# Build the docs using Doxygen
docs:
	cmake -E chdir docs doxygen -q

.PHONY: build configure flash attach attach_reset clean docs
