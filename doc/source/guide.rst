.. py:currentmodule:: tinysoundfont
 
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

What you might want to use this package for:

* Play MIDI files with SoundFonts in Python
* Play MIDI files with modifications and customizations (mute tracks, change instruments, etc.)
* Procedurally generate and play music or sounds
* Play music and sounds in an interative way in your Python program

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


To install `tinysoundfont`, for all platforms do:

.. code-block:: bash

   pip install tinysoundfont

If you have a less common platform then binary wheels may not be available. In
this case `pip` will attempt to build the package locally from the source
distribution so you will need to have a working local development environment
installed.

Getting SoundFonts
------------------

Example Organ
^^^^^^^^^^^^^

In order to use this package to do anything interesting you need at least one
SoundFont. For testing purposes this package contains a small SoundFont that can
be downloaded: `example.sf2
<https://github.com/nwhitehead/tinysoundfont-pybind/raw/main/test/example.sf2>`_

This example SoundFont contains a single instrument, an artificial organ with
preset name "El Cheapo Organ".

GM SoundFont `FluidR3_GM`
^^^^^^^^^^^^^^^^^^^^^^^^^

Many SoundFonts aim to cover all 128 of the `General MIDI
<https://en.wikipedia.org/wiki/General_MIDI>`_ instruments. This allows playback
of any MIDI file that uses the same General MIDI standard. Other SoundFonts are
designed to provide instruments that represent specific physical instruments,
vintage synthesizers, retro video game console systems, or other types of
stylized sounds.

FluidSynth works with a Creative Commons licensed SoundFont named `FluidR3_GM
<https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip>`_. This SoundFont is
good for general MIDI music playback.

Online Resources
^^^^^^^^^^^^^^^^

Because SoundFonts have been around for decades searching the web for terms
such as "SoundFont", "SF2" or more specific terms like "soundfont sf2 piano"
usually leads to many results. SoundFonts found online may be of random quality
and may or may not be licensed in a way that suites your use of the download
(be careful).

For specific instruments a good resource is the `Polyphone Soundfonts page
<https://www.polyphone-soundfonts.com/download-soundfonts>`_. This page
lets you browse by instrument category and see reviews and comments by
users.

There are many lists of SoundFont downloads online. One resource is
`SynthFont Links <http://www.synthfont.com/links_to_soundfonts.html>`_.

Play a Note
-----------

To play a note and hear it, the general steps are:

1. Create a :class:`Synth` object
2. Call :meth:`Synth.sfload` to load a SoundFont instrument
3. Select a specific bank/preset in the instrument with :meth:`Synth.program_select`
4. Turn on a note with :meth:`Synth.noteon`
5. Start the audio callback thread with :meth:`Synth.start`
6. Wait to exit your program, maybe call :func:`time.sleep`

There is some flexibility in the order of steps. For example you could start the
audio callback thread first and then select bank/preset and turn on the note.

Here is a tiny example program to play a note:

.. literalinclude:: ../../test/example_one_note.py

Play a Chord
------------

One SoundFont instrument can play multiple notes at the same time in the same MIDI channel. To play
a chord call :meth:`Synth.noteon` for multiple keys.

Here is an example that plays a single chord.

.. literalinclude:: ../../test/example_chord.py

.. include:: note_sleep.rstinc

Change Instruments
------------------

One SoundFont can contain many instruments. This example shows playing notes
from different instruments in the `FluidR3_GM` SoundFont.

.. literalinclude:: ../../test/example_instruments.py

.. include:: note_sleep.rstinc

.. include:: note_fluidr3.rstinc


Play a MIDI
-----------

This example plays a MIDI file using a General MIDI SoundFont. It schedules the
song to play then waits until the song is finished and ends.

.. literalinclude:: ../../test/example_song.py

.. include:: note_fluidr3.rstinc

Control MIDI
------------

This example plays a MIDI file using the example SoundFont. It filters the MIDI
instrument changes to only use preset `0` for all channels.

.. literalinclude:: ../../test/example_midi_filter.py

