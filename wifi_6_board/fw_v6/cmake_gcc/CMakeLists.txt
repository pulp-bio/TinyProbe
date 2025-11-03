# Define minimal required version of CMake.
cmake_minimum_required(VERSION "3.25")

# Project definition
project(
	fw_v6
	VERSION 1.0
	LANGUAGES C CXX ASM
)

# Include the definition of the slc_fw_v6 target,
# which contains the content of the SLC project
include(fw_v6.cmake)

add_executable(fw_v6
    # Add additional sources here
)

target_include_directories(fw_v6 PUBLIC
    # Add additional include paths here
)

target_compile_definitions(fw_v6 PUBLIC
    # Add additional macros here
)

target_compile_options(fw_v6 PUBLIC
    # Set additional compiler flags here
)

target_link_options(fw_v6 PUBLIC
    # Set additional linker flags here
)

# Link with the content defined in the SLC project
target_link_libraries(fw_v6 PRIVATE
    slc
)

# Include managed project content if available
include(fw_v6_project.cmake OPTIONAL RESULT_VARIABLE managed_project)
if(managed_project)
    message(STATUS "Using managed project content from ${managed_project}")
endif()

# Force the gcc linker command
set_target_properties(fw_v6 PROPERTIES LINKER_LANGUAGE C)

# Create .bin, .hex and .s37 artifacts after building the project
add_custom_command(TARGET fw_v6
    POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} ${OBJCOPY_SREC_CMD} "$<TARGET_FILE:fw_v6>" "$<TARGET_FILE_DIR:fw_v6>/$<TARGET_FILE_BASE_NAME:fw_v6>.s37"
    COMMAND ${CMAKE_OBJCOPY} ${OBJCOPY_IHEX_CMD} "$<TARGET_FILE:fw_v6>" "$<TARGET_FILE_DIR:fw_v6>/$<TARGET_FILE_BASE_NAME:fw_v6>.hex"
    COMMAND ${CMAKE_OBJCOPY} ${OBJCOPY_BIN_CMD}  "$<TARGET_FILE:fw_v6>" "$<TARGET_FILE_DIR:fw_v6>/$<TARGET_FILE_BASE_NAME:fw_v6>.bin" 
)

# Run post-build pipeline to perform additional post-processing
if(post_build_command)
add_custom_command(TARGET fw_v6
    POST_BUILD
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/..
    COMMAND ${post_build_command}
)
endif()