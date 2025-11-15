cmake_minimum_required(VERSION 3.16)
project(AgroScout LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Sql Test)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Sql Test)

# Основной исполняемый файл
add_executable(AgroScout
    src/db/sqlitedb/sqlitedb.cpp
    src/db/sqlitedb/sqlitedb.h
    include/dbinterface/dbinterface.h
    include/config/config.h
    include/status/statuscodes.h
    include/status/statusmapper.h
    include/status/logmessages.h
    src/sql/schema.sql
)

target_include_directories(AgroScout PRIVATE
    include
    src
    src/db/sqlitedb
    src/sql
)

target_link_libraries(AgroScout
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Sql
)

# Тестовый таргет
add_executable(AgroScoutTests
    src/tests/sqlitedbtest/dbtests.cpp
    src/db/sqlitedb/sqlitedb.cpp
    src/db/sqlitedb/sqlitedb.h
    include/dbinterface/dbinterface.h
    include/config/config.h
    include/status/statuscodes.h
    include/status/statusmapper.h
    include/status/logmessages.h
    src/sql/schema.sql
)

target_include_directories(AgroScoutTests PRIVATE
    include
    src
    src/db/sqlitedb
    src/tests/sqlitedbtest
    src/sql
)

target_link_libraries(AgroScoutTests
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Sql
    Qt${QT_VERSION_MAJOR}::Test
)

# Установка основного исполняемого файла
include(GNUInstallDirs)
install(TARGETS AgroScout
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
