# PyTinySoundFont

Play SoundFont instruments (SF2) using Python.

## Installation

## Usage

Each SF2 instrument is loaded into its own object:

    sf = tinysoundfont.SoundFont('test/example.sf2')

Setup the output format and global volume:

    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)

The negative global gain lets multiple notes mix without distortion.

Play a note with:

    # Play preset 0, MIDI note 80, at full velocity
    sf.note_on(0, 80, 1.0)

Create a buffer for the instrument to render to. This buffer can be anything
that follows the Python "buffer protocol". For example, this can be objects of
type `bytearray`, `numpy.ndarray`, and many other things. The buffer can be 1D
or 2D. If it is 1D then it is expected to be a simple contiguous array of bytes
that will be filled with audio samples. If it is 2D then it is expected to have
correct format type `float32` and dimensions `(samples, channels)` where
`channels` will be 1 (mono) or 2 (stereo). Samples are always in `float32`
format.

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
