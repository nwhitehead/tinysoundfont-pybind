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

Compressed audio is handled by `std_vorbis.c
<https://github.com/nothings/stb/blob/master/stb_vorbis.c>`_.

MIDI
----

Low-level MIDI decoding is handled by `tml.h` which is included in
`TinySoundFont`. From there some code in `main.cpp` goes through the MIDI events
and constructs a Python list of dictionaries with appropriate keys for passing
to Python. This data structure is converted to a nicer representation that uses
Python `dataclasses`.

Development local build and test
--------------------------------

Note that a local build and test is not required to use the package, only for
developing `tinysoundfont` itself.

Build and install locally with:

.. code-block:: text

    python -m pip install .

Test in the root directory with:

.. code-block:: text

    pytest

You may want to build and test in a `virtualenv` environment.

The `python -m pip install .` will perform a compilation step for `C++` code.
Your environment must have access to a working `C++` compiler as well as the
Python development headers.

Editable build
--------------

To speed up development you can do an "editable build". This will cache a lot of
compiling and setup. First install all needed dependencies in `pip`:

.. code-block:: text

    pip install scikit_build_core pyproject_metadata pathspec pybind11

Then install with `editable.rebuild` on:

.. code-block:: text

    pip install . --no-build-isolation --config-setting=editable.rebuild=true -Cbuild-dir=build .

In my experience you still need to rerun this command when editing files, but it
will go faster.

Packaging
---------

Building wheels for PyPI is done by GitHub Actions and does not need to be done
manually.

Documentation
-------------

Documentation is done using `Sphinx <https://www.sphinx-doc.org/en/master/>`_.
GitHub Actions builds automatically and pushes pages to the `Documentation Page
<https://nwhitehead.github.io/tinysoundfont-pybind/>`_.
