# TinySoundFont-pybind

This `tinysoundfont` Python package provides Python bindings for
[TinySoundFont](https://github.com/schellingb/TinySoundFont) and lets you
generate audio using SoundFont instruments (`.sf2`, `.sf3`, or `.sfo` files) in
Python. The audio data can be played by
[PyAudio](https://pypi.org/project/PyAudio/) in a separate thread if requested.
This package also includes support for loading and playing MIDI data using a
SoundFont instrument.

What you might want to use this package for:

* Play MIDI files with SoundFonts in Python
* Play MIDI files with modifications and customizations (mute tracks, change instruments, etc.)
* Procedurally generate and play music or sounds
* Play music and sounds in an interactive way in your Python program

## Documentation

[Main `tinysoundfont` documentation](https://nwhitehead.github.io/tinysoundfont-pybind/)

The documentation contains:
* [Guide](https://nwhitehead.github.io/tinysoundfont-pybind/guide.html)
* [API Reference](https://nwhitehead.github.io/tinysoundfont-pybind/reference.html)

## Installation

This package depends on `pyaudio` for playing sounds. To install `pyaudio` for
common platforms:

### Windows

    python -m pip install pyaudio

### macOS

    brew install portaudio
    pip install pyaudio

### GNU/Linux (Ubuntu)

    sudo apt install python3-pyaudio

To install `tinysoundfont`, for all platforms do:

    pip install tinysoundfont


## Basic Usage

Here is an example program that plays a chord:

    import tinysoundfont
    import time

    synth = tinysoundfont.Synth()
    sfid = synth.sfload("florestan-piano.sf2")
    synth.program_select(0, sfid, 0, 0)
    synth.start()

    time.sleep(0.5)

    synth.noteon(0, 48, 100)
    synth.noteon(0, 52, 100)
    synth.noteon(0, 55, 100)

    time.sleep(0.5)

    synth.noteoff(0, 48)
    synth.noteoff(0, 52)
    synth.noteoff(0, 55)

    time.sleep(0.5)

Please see the [Guide](https://nwhitehead.github.io/tinysoundfont-pybind/guide.html)
for more examples and notes about the examples.

## Local build and test

Note that a local build and test is not required to use the package,
only for developing `tinysoundfont` itself.

Build and install locally with:

    python -m pip install .

Test in the root directory with:

    pytest

You may want to build and test in a `virtualenv` environment.

The `python -m pip install .` will perform a compilation step for `C++` code. Your
environment must have access to a working `C++` compiler as well as the Python
development headers.

### Editable build

To speed up development you can do an "editable build". This will cache a lot of
compiling and setup. First install all needed dependencies in `pip`:

    pip install scikit_build_core pyproject_metadata pathspec pybind11

Then install with `editable.rebuild` on:

    pip install . --no-build-isolation --config-setting=editable.rebuild=true -Cbuild-dir=build .

In my experience you still need to rerun this command when editing files, but it will go faster.

### Packaging

Building wheels for PyPI is done by GitHub Actions and does not need to be done manually.

### Documentation

Documentation is done using [Sphinx](https://www.sphinx-doc.org/en/master/).
