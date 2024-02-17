
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.1.0"

setup(
    ext_modules=[
        Pybind11Extension(
            "tinysoundfont",
            ["src/main.cpp"],
            define_macros=[("VERSION_INFO", __version__)],
            cxx_std=17,
        ),
    ],
)
