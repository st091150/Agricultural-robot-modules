cmake_minimum_required(VERSION 3.30)
project(robot LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 6.5 REQUIRED COMPONENTS Core Network)

add_library(net
        src/network/Base.h
        src/network/Tcp.cc
        src/network/Udp.cc
        src/network/Http.cc
)
target_include_directories(net PUBLIC include)
target_link_libraries(net PUBLIC Qt6::Core Qt6::Network)

#add_executable(client main.cpp)
#target_link_libraris(client PRIVATE net Qt6::Core Qt6::Network)

#add_executable(server src/server.cpp)
#target_link_libraries(server PRIVATE net Qt6::Core Qt6::Network net)
