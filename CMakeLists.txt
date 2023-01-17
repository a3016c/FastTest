cmake_minimum_required(VERSION 2.8.6)
project (FastTest)
set (CMAKE_BUILD_TYPE Debug)
set(CMAKE_OSX_ARCHITECTURES "x86_64")

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/build)

include_directories (include ${CMAKE_SOURCE_DIR}/include)

#compile all *.cpp source files under src folder
file (GLOB SOURCES "src/*.cpp")

#output library export file *.lib and
#output macro definitions include file
include (GenerateExportHeader)

add_library(FastTest SHARED ${SOURCES})
GENERATE_EXPORT_HEADER (FastTest
    BASE_NAME FastTest
    EXPORT_MACRO_NAME FastTest_EXPORT
    EXPORT_FILE_NAME FastTest_EXPORT.h
    STATIC_DEFINE FastTest_BUILT_AS_STATIC
)

IF( NOT CMAKE_BUILD_TYPE )
   SET( CMAKE_BUILD_TYPE Release ... FORCE )
   message("RELEASE BUILD...")
ENDIF()

target_compile_options(FastTest PRIVATE -std=c++20 -fdeclspec -O3)
