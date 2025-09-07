add_library(wius STATIC
    wius_gpio.c
    wius_spi.c
    wius_udp.c
    wius_wifi.c
    wius_power.c
)
target_include_directories(wius PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(wius PUBLIC
    slc_wius_fw
    common
)