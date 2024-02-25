from skbuild import setup

setup(
    name = "tinysoundfont",
    version="0.2.3",
    packages=['tinysoundfont'],
    author= "Nathan Whitehead <nwhitehe@gmail.com>",
    description = "Python bindings for using Sound Fonts (sf2/sf3/sfo formats) and generating audio samples",
    readme = "README.md",
    python_requires = ">=3.7",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)

