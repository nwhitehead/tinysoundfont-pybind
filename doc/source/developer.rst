Developer Notes
================================================

The package provides Python bindings for the C library `TinySoundFont
<https://github.com/schellingb/TinySoundFont>`_.

Internally, Python bindings are created using `pybind11
<https://github.com/pybind/pybind11>`_ to native code that is part of the
package. That means this package is self-contained and does not link to any
other native libraries.

The `Guide` talks about the goals of `tinysoundfont`. Things that are *not*
goals of `tinysoundfont`:

1. To cover general audo synthesis algorithms and digital effects
2. To be exhaustive in duplicating the `FluidSynth` API
3. To control general MIDI signal routing and input/output
4. To provide guaranteed real-time responsiveness without glitches
5. To be an editor or validator for SoundFonts

Compression
-----------

Compressed audio is handled by `std_vorbis.c <https://github.com/nothings/stb/blob/master/stb_vorbis.c>`_.

MIDI
----

Low-level MIDI decoding is handled by `tml.h` which is included in `TinySoundFont`. From there some code
in `main.cpp` goes through the MIDI events and constructs a Python list of dictionaries with appropriate
keys for passing to Python. This data structure is converted to a nicer representation that uses Python
`dataclasses`.
