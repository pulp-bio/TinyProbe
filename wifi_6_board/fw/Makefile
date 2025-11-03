PROJECT = wius_fw

CMAKE_DIR = $(PROJECT)_cmake
BUILD_DIR = build
PYTHON = python
COMMANDER = "C:/Users/cedr0/.silabs/slt/installs/archive/Simplicity Commander/commander.exe"

TARGET = $(CMAKE_DIR)/$(BUILD_DIR)/default_config/$(PROJECT).hex

all: build

build:
	cd $(CMAKE_DIR) && cmake --build $(BUILD_DIR)

clean:
	rm -rf $(CMAKE_DIR)/$(BUILD_DIR) env.h

$(CMAKE_DIR)/$(BUILD_DIR): $(CMAKE_DIR)/CMakeLists.txt env.h
	cd $(CMAKE_DIR) && cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON --preset project

env.h: .env
	$(PYTHON) scripts/fetch_env.py $< $@

flash: build
	$(COMMANDER) flash $(TARGET)

.PHONY: all clean flash build