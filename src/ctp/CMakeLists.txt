# 1. 定义下载地址和保存路径
set(LIB_URL "https://github.com/Edanflame/chocotrade/releases/download/v0.1.1/CTP_6.7.7_MAC.zip")
set(LIB_DEST "${CMAKE_SOURCE_DIR}/src/ctp/CTP_6.7.7_MAC.zip")
set(LIB_DIR "${CMAKE_SOURCE_DIR}/src/ctp")

# 2. 检查本地是否已经有库文件
if(NOT EXISTS "${LIB_DIR}/libs/thostmduserapi_se.framework")
    message(STATUS "正在从远程下载 CTP 二进制库...")
    
    # 下载文件
    file(DOWNLOAD ${LIB_URL} ${LIB_DEST} SHOW_PROGRESS)
    
    # 解压文件（如果是 .tar.gz 或 .zip）
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E tar xzf ${LIB_DEST}
        WORKING_DIRECTORY ${LIB_DIR}
    )

    file(RENAME "${CMAKE_SOURCE_DIR}/src/ctp/CTP_6.7.7_MAC/" "${CMAKE_SOURCE_DIR}/src/ctp/libs/")

    # 删除压缩包（可选）
    file(REMOVE ${LIB_DEST})
endif()


# 3.开始编译ctp
pybind11_add_module(ctpmd ctpmd.cpp)
pybind11_add_module(ctptd ctptd.cpp)

# 设置框架的搜索目录（假设在项目根目录的 libs 文件夹下）
set(CMAKE_FRAMEWORK_PATH ${CMAKE_SOURCE_DIR}/src/ctp/libs)

# 寻找你的框架
find_library(MD_API_LIB thostmduserapi_se)
find_library(TD_API_LIB thosttraderapi_se)

set_target_properties(ctpmd PROPERTIES
    BUILD_WITH_INSTALL_RPATH TRUE
    INSTALL_RPATH "@loader_path;@loader_path/ctp/libs"
)

set_target_properties(ctptd PROPERTIES
    BUILD_WITH_INSTALL_RPATH TRUE
    INSTALL_RPATH "@loader_path;@loader_path/ctp/libs"
)

# 链接
target_link_libraries(ctpmd PRIVATE ${MD_API_LIB})
target_link_libraries(ctptd PRIVATE ${TD_API_LIB})

# 头文件搜索路径
target_include_directories(ctpmd PUBLIC
    ${CMAKE_SOURCE_DIR}/src/ctp/include
)
target_include_directories(ctptd PUBLIC
    ${CMAKE_SOURCE_DIR}/src/ctp/include
)

# 安装
install(TARGETS ctpmd ctptd LIBRARY DESTINATION chocotrade/src)

# 拷贝lib文件，动态链接
install(DIRECTORY "${CMAKE_SOURCE_DIR}/src/ctp/libs"
    DESTINATION chocotrade/src/ctp
)
