cmake_minimum_required( VERSION 3.15...3.26 )

project( ${SKBUILD_PROJECT_NAME} LANGUAGES CXX )

set( PYBIND11_NEWPYTHON ON )
set( CMAKE_CXX_STANDARD 14 CACHE STRING "C++ version selection" )

find_package( pybind11 CONFIG REQUIRED )

pybind11_add_module(
    _tinysoundfont
    src/_tinysoundfont/main.cpp
)

install(
    TARGETS
        _tinysoundfont
    LIBRARY DESTINATION
        ./tinysoundfont
)
