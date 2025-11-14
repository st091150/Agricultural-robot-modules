cmake_minimum_required(VERSION 3.16)
project(AgroScout LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Sql)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Sql)

# Основной исполняемый файл
add_executable(AgroScout
    src/db/sqlitedb.cpp
    src/db/sqlitedb.h
    include/dbinterface/dbinterface.h
    include/config/config.h
    include/status/statuscodes.h
    include/status/statusmapper.h
    include/status/logmessages.h
    sql/schema.sql
)

target_include_directories(AgroScout PRIVATE include src)

target_link_libraries(AgroScout
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Sql
)

# Установка исполняемого файла
include(GNUInstallDirs)
install(TARGETS AgroScout
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
