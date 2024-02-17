# PyTinySoundFont

This project is a Python package that provides Python bindings for
[TinySoundFont](https://github.com/schellingb/TinySoundFont). This lets you
generate audio using SoundFont instruments (`.sf2`) in Python.

Python bindings are created using
[pybind11](https://github.com/pybind/pybind11).

## Installation

To install from source in this repository, clone this repository then do:

    pip install .

## Basic Usage

Each SF2 instrument is loaded into its own object:

    sf = tinysoundfont.SoundFont('test/example.sf2')

Setup the output format and global volume:

    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)

The negative global gain lets multiple notes mix without distortion. The correct value to use
will depend on how many notes you expect to play and the gain settings of the particular `sf2`
instrument.

Play a note with:

    # Play preset 0, MIDI note 80, at full velocity
    sf.note_on(0, 80, 1.0)

Now create a buffer for the instrument to render to. This buffer can be anything
that follows the Python buffer protocol. For example, this can be objects of
type `bytearray`, `numpy.ndarray`, and many other things. The buffer can be 1D
or 2D. If it is 1D then it is expected to be a simple contiguous array of bytes
that will be filled with audio samples. If it is 2D then it is expected to have
correct format type `float32` and dimensions `(samples, channels)` where
`channels` will be 1 (mono) or 2 (stereo). Samples are always in `float32`
format.

    # Create 1 second buffer for stereo float32 at 44.1 KHz
    buffer = bytearray(44100 * 4 * 2)

Generate samples using:

    sf.render(buffer)

The buffer now contains audio data for the playing instrument.

## Playing sound

To get actual sound you need something like `pyaudio`.

## Local build and test

Build and install locally with:

    pip install .

Test with:

    python test/simple.py

You may want to build/test in a `venv` environment.

## Compressed SoundFonts

A compressed SoundFont2 format `.sfo` is also supported through
[std_vorbis.c](https://github.com/nothings/stb/blob/master/stb_vorbis.c). The
compressed `.sfo` format is similar to regular `.sf2` but the audio waveforms
are stored with Ogg/Vorbis compression instead of being stored uncompressed.
This is especially useful for large General MIDI soundbanks that contain many
instruments in one file. For information about converting SoundFonts see
[SFOTool](https://github.com/schellingb/TinySoundFont/tree/master/sfotool).
