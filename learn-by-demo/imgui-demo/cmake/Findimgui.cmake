find_package(glfw REQUIRED)

include(FetchContent)

FetchContent_Declare(imgui
    GIT_REPOSITORY      https://github.com/ocornut/imgui.git
    GIT_TAG             docking
)
FetchContent_Populate(imgui)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(imgui DEFAULT_MSG
    imgui_POPULATED
)

add_library(imgui
    ${imgui_SOURCE_DIR}/imgui.cpp
    ${imgui_SOURCE_DIR}/imgui_demo.cpp
    ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_glfw.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp
)
target_include_directories(imgui PUBLIC ${imgui_SOURCE_DIR} ${imgui_SOURCE_DIR}/backends)
target_link_libraries(imgui PUBLIC glfw)
