Guide
================================================

This is a short guide to using `tinysoundfont`.

What is it?
-----------

The `tinysoundfont` Python package lets you generate audio using SoundFont
instruments (`.sf2`, `.sf3`, or `.sfo` files) in Python. The audio data can be
played by `PyAudio <https://pypi.org/project/PyAudio/>`_ in a separate thread if
requested. This package also includes support for loading and playing MIDI data
using a SoundFont instrument.

You can use this package to play MIDI files with SoundFonts using Python.
This package can also be used for procedural generation of music or other kinds
of musical experiments.

Goals
-----

The goals of `tinysoundfont` are:

1. To be easy to install with as few native dependencies as possible
2. To allow for note generation and musical experimentation quickly with minimal code
3. To provide an API that is as consistent as practical with other similar APIs such as `FluidSynth <https://www.fluidsynth.org/api/Introduction.html>`_.
4. To have permissive licensing (MIT)

Installation
------------

This package depends on `pyaudio` for playing sounds. To install
`pyaudio` for common platforms:

.. tabs::

   .. tab:: Windows

      .. code-block:: bash

         python -m pip install pyaudio

   .. tab:: MacOS

      .. code-block:: bash

         brew install portaudio
         pip install pyaudio

   .. tab:: Linux (Ubuntu)

      .. code-block:: bash

         sudo apt install python3-pyaudio


To install this package, for all platforms do:

.. code-block:: bash

   pip install tinysoundfont

If you have a less common platform then binary wheels may not be available. In
this case `pip` will attempt to build the package locally from the source
distribution.

Getting SoundFonts
------------------

In order to use this package to do anything interesting you need some SoundFonts.
For testing purposes this package contains a small SoundFont that can be downloaded:
https://github.com/nwhitehead/tinysoundfont-pybind/raw/main/test/example.sf2

This example SoundFont contains a single instrument, an artificial organ with preset
name "El Cheapo Organ".

Many SoundFonts aim to cover all 128 of the `General MIDI
<https://en.wikipedia.org/wiki/General_MIDI>` instruments. This allows playback
of any MIDI file that uses the same General MIDI standard.



Play a Note
-----------

To play a note and hear it, the general steps are:

1. Create a :class:`tinysoundfont.Synth` object
2. Call :meth:`tinysoundfont.Synth.sfload` to load a SoundFont instrument
3. Start the audio callback thread with :meth:`tinysoundfont.Synth.start`
4. Select a specific bank/preset in the instrument with :meth:`tinysoundfont.Synth.program_select`
5. Turn on a note with :meth:`tinysoundfont.Synth.noteon`
6. Wait to exit your program, maybe call :func:`time.sleep`

