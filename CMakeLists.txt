
cmake_minimum_required(VERSION 3.15)
project(chocotrade LANGUAGES CXX)

# 找 pybind11
find_package(pybind11 REQUIRED)

# 添加子目录
add_subdirectory(src/module1)
add_subdirectory(src/cpp_data_structures)
add_subdirectory(src/ctp)
