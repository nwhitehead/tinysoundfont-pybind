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

Some advantages of this package specifically compared to some others:

* Permissive MIT licensing that works well with commercial products like games
* No dependencies on other installed libraries for audio data generation

## Documentation

[Main `tinysoundfont` documentation](https://nwhitehead.github.io/tinysoundfont-pybind/)

The documentation contains:
* [Guide](https://nwhitehead.github.io/tinysoundfont-pybind/guide.html)
* [API Reference](https://nwhitehead.github.io/tinysoundfont-pybind/reference.html)

## Installation

This package depends on `pyaudio` for playing sounds. To install `pyaudio` and
`tinysoundfont` for common platforms:

### Windows

    py -m pip install pyaudio tinysoundfont

### macOS

    brew install portaudio
    pip install pyaudio tinysoundfont

### GNU/Linux (Ubuntu)

    sudo apt install python3-pyaudio
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

Please see the
[Guide](https://nwhitehead.github.io/tinysoundfont-pybind/guide.html) for more
examples and notes about the examples.

## Command line

The `tinysoundfont` package contains a simple command line tool that can
be useful for finding presets, testing the validity of SoundFonts, and
playing MIDI files.

Here is an example that loads the demo SoundFont and shows the presets it defines:

    python -m tinysoundfont --info florestan-subset.sfo

(In Windows you may need to use `py` instead of `python`).

This results in:

    Info for SoundFont florestan-subset.sfo
    0 - 2 : Piano
    0 - 10 : Music Box
    0 - 12 : Marimba
    0 - 19 : Church Org.1
    0 - 21 : Accordion Fr
    0 - 24 : Nylon-str.Gt
    0 - 38 : Synth Bass 1
    0 - 40 : Violin
    0 - 45 : PizzicatoStr
    0 - 55 : OrchestraHit
    0 - 61 : Brass 1
    0 - 75 : Pan Flute
    0 - 87 : Bass & Lead
    0 - 90 : Polysynth
    0 - 97 : Soundtrack
    0 - 109 : Bagpipe
    0 - 116 : Taiko

The output format shows `bank - preset : Name`.

Here is an example that plays a test note using preset `55`:

    python -m tinysoundfont --test florestan-subset.sfo --preset 55 --key 70

Here is an example that plays a MIDI file using the `FluidR3_GM` SoundFont:

    python -m tinysoundfont --play FluidR3_GM.sf2 1080-c01.mid

## License

This project is MIT licensed, see
[LICENSE](https://github.com/nwhitehead/tinysoundfont-pybind/blob/main/LICENSE).
For full license information about dependencies and test files included in this
repository, see
[NOTICE](https://github.com/nwhitehead/tinysoundfont-pybind/blob/main/NOTICE).

## Contributing

If you have ideas for features, bug fixes, or other things please use Github
and contribute! If something doesn't work or seems wrong please file an issue.
