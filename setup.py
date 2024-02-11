
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.1"

ext_modules = [
    Pybind11Extension(
        "tinysoundfont",
        ["src/main.cpp"],
        define_macros=[("VERSION_INFO", __version__)],
        cxx_std=17,
    ),
]

setup(
    name="TinySoundFont",
    version=__version__,
    author="Nathan Whitehead",
    author_email="nwhitehe@gmail.com",
    url="",
    description="Python bindings for loading Sound Fonts (sf2 format) and generating audio samples",
    long_description="",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    zip_safe=False,
    python_requires=">=3.7",
)
