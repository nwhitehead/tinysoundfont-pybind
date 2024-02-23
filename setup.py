
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

setup(
    ext_modules=[
        Pybind11Extension(
            "tinysoundfont",
            ["src/main.cpp"],
            cxx_std=14,
        ),
    ],
)
