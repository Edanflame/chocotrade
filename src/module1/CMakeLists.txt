pybind11_add_module(my_module1 main.cpp test.cpp)

# 头文件搜索路径
target_include_directories(my_module1 PUBLIC
    ${CMAKE_SOURCE_DIR}/src/module1/include
)

install(TARGETS my_module1 LIBRARY DESTINATION chocotrade/src)
