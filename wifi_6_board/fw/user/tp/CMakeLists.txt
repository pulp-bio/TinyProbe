add_library(tinyprobe STATIC
    tp_afe.o
    tp_buffer.c
    tp_command.c
    tp_fpga.c
    tp_mux.c
    tp_power.c
    tp_tx.c
    tp.c
)
target_include_directories(tinyprobe PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(tinyprobe PUBLIC
    slc_wius_fw
    common
)