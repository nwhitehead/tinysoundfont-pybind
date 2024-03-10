Developer Notes
================================================

The package provides Python bindings for the C library `TinySoundFont
<https://github.com/schellingb/TinySoundFont>`_.

Internally, Python bindings are created using `pybind11
<https://github.com/pybind/pybind11>`_ to native code that is part of the
package. That means this package is self-contained and does not link to any
other native libraries.

Things that are *not* goals of `tinysoundfont`:

1. To cover general audo synthesis algorithms and digital effects
2. To be exhaustive in duplicating the `FluidSynth` API
3. To control general MIDI signal routing and input/output
4. To provide guaranteed real-time responsiveness without glitches
