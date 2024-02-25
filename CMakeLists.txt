cmake_minimum_required(VERSION 3.18...3.22)

project(tinysoundfont)

find_package(PythonExtensions REQUIRED)

add_library(_tinysoundfont MODULE tinysoundfont/main.cpp)
python_extension_module(_tinysoundfont)
install(TARGETS _tinysoundfont LIBRARY DESTINATION tinysoundfont)
