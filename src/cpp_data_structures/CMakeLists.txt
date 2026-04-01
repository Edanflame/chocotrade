pybind11_add_module(cpp_data_structures main.cpp data_structures.cpp)

target_include_directories(cpp_data_structures PUBLIC
  ${CMAKE_SOURCE_DIR}/src/cpp_data_structures/include
)

install(TARGETS cpp_data_structures LIBRARY DESTINATION chocotrade/src)
