add_subdirectory(tp)
add_subdirectory(wius)

add_library(common STATIC
    common.c
    log.c
    user.c
)
target_include_directories(common PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(common PUBLIC
    wius tinyprobe
)