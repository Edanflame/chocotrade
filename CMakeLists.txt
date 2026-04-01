
cmake_minimum_required(VERSION 3.15)
project(my_package LANGUAGES CXX)

# 找 pybind11
find_package(pybind11 REQUIRED)

# 添加子目录
add_subdirectory(src/module1)
add_subdirectory(src/cpp_data_structures)
