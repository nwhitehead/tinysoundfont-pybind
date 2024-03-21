.. py:currentmodule:: tinysoundfont
 
Guide
================================================

This is a short guide to using `tinysoundfont`. If you want details on specific
API functions look in the :doc:`reference`.

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
* Play music and sounds in an interactive way in your Python program

Goals
-----

The goals of `tinysoundfont` are:

1. To be easy to install with as few native dependencies as possible
2. To allow for note generation and musical experimentation quickly with minimal code
3. To provide a consistent API
4. To have permissive licensing (MIT) 

Installation
------------

This package depends on `pyaudio` for playing sounds. To install
`pyaudio` for common platforms:

.. tabs::

   .. tab:: Windows

      .. code-block:: bash

         py -m pip install pyaudio

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

Example Piano
^^^^^^^^^^^^^

In order to use this package to do anything interesting you need at least one
SoundFont. For testing purposes this package contains a small SoundFont that can
be downloaded:

`florestan-piano.sf2
<https://github.com/nwhitehead/tinysoundfont-pybind/raw/main/test/florestan-piano.sf2>`_

This example SoundFont contains a single instrument, an artificial piano.

Example Compressed SoundFont
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To demonstrate compressed SoundFonts, this package contains a small collection
of 17 instruments in compressed format that can be downloaded at: 

`florestan-subset.sfo
<https://github.com/nwhitehead/tinysoundfont-pybind/raw/main/test/florestan-subset.sfo>`_

Even though this SoundFont contains the piano instrument and 16 other instruments,
the total file size is smaller than `florestan-piano.sf2` in uncompressed format.

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

MuseScore
^^^^^^^^^

Another source of freely available SoundFonts is the MuseScore project. The
`MuseScore Handbook: SoundFonts and SFZ Files
<https://musescore.org/en/handbook/3/soundfonts-and-sfz-files#list>`_ page
includes links to download various `SF2` and `SF3` SoundFonts that have been
used in various versions of MuseScore.

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

Compressing SoundFonts
^^^^^^^^^^^^^^^^^^^^^^

This package also supports compressed SoundFont2 formats `.sf3` and `.sfo`. The
compressed formats are similar to regular `.sf2` but the audio waveforms are
stored with Ogg/Vorbis compression instead of being stored uncompressed. This is
especially useful for large General MIDI soundbanks that contain many
instruments in one file. For information about converting SoundFonts see
`SFOTool <https://github.com/schellingb/TinySoundFont/tree/master/sfotool>`_.

Compressed streams are decompressed into memory when the file is loaded. This
means there will be more computation required when loading the instrument. This
also means the total memory needed at runtime will not be less than the
equivalent uncompressed `.sf2` version. The compressed format is more for saving
space when distributing or storing the instrument file.

Another consideration is unused samples and instruments. It may make sense for
your application to start with a large General MIDI SoundFont and then edit it
to only include the instruments and sounds you actually use. The application
`Polyphone <https://www.polyphone-soundfonts.com/>`_ can be used to edit
SoundFonts. The application cannot edit `.sfo` format, so you should use SFOTool
to compress the SoundFont after editing with Polyphone.

Examples
--------

Play a note
^^^^^^^^^^^

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

.. include:: note_piano.rstinc

Play a Chord
^^^^^^^^^^^^

One SoundFont instrument can play multiple notes at the same time in the same MIDI channel. To play
a chord call :meth:`Synth.noteon` for multiple keys.

Here is an example that plays a single chord.

.. literalinclude:: ../../test/example_chord.py

.. include:: note_sleep.rstinc

.. include:: note_piano.rstinc

Change Instruments
^^^^^^^^^^^^^^^^^^

One SoundFont can contain many instruments. This example shows playing notes
from different instruments in the `florestan-subset.sfo` compressed SoundFont.

.. literalinclude:: ../../test/example_instruments.py

.. include:: note_sleep.rstinc

.. include:: note_florestan.rstinc


Play a MIDI File
^^^^^^^^^^^^^^^^

This example plays a MIDI file using a General MIDI SoundFont. It schedules the
song to play then waits until the song is finished and ends.

.. literalinclude:: ../../test/example_song.py

.. include:: note_fluidr3.rstinc

.. include:: note_1080.rstinc

Filter MIDI Events
^^^^^^^^^^^^^^^^^^

This example plays a MIDI file using the `florestan_subset.sfo` compressed
example SoundFont. It filters the MIDI instrument changes in the multi-channel
song to only use preset `19` (Church Organ) for all channels.

The MIDI file uses MIDI GM presets `40` to `43` (or presets `41` through `44` in
1-based indexing). The `florestan_subset.sfo` SoundFont only contains preset
`40`. Without any MIDI filtering the playback would start with violin but later
parts using cello and contrabass would default to a piano sound.

.. literalinclude:: ../../test/example_midi_filter.py

.. include:: note_florestan.rstinc

.. include:: note_1080.rstinc

Drum Sounds
^^^^^^^^^^^

The General MIDI convention is that drum events happens on channel 10. You can
set any channel to be a drum kit channel using :meth:`Synth.program_select` or
:meth:`Synth.program_change`. A drum kit channel maps each MIDI key of the
channel to different drum instruments. For example key `36` is a bass drum and
`56` is a cowbell.

This example plays a short drum pattern.

.. literalinclude:: ../../test/example_drums.py

.. include:: note_fluidr3.rstinc

.. include:: note_drum_midi.rstinc

Topics
------

Command Line Tool
^^^^^^^^^^^^^^^^^

The `tinysoundfont` package contains a simple command line tool that can
be useful for finding presets, testing the validity of SoundFonts, and
playing MIDI files.

Here is an example that loads the demo SoundFont and shows the presets it defines:

.. code-block:: text

   python -m tinysoundfont --info florestan-subset.sfo

(In Windows you may need to use `py` instead of `python`).

This results in:

.. code-block:: text

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

.. code-block:: text

   python -m tinysoundfont --test florestan-subset.sfo --preset 55 --key 70

Here is an example that plays a MIDI file using the `FluidR3_GM` SoundFont:

.. code-block:: text

   python -m tinysoundfont --play FluidR3_GM.sf2 1080-c01.mid

Latency
^^^^^^^

If you don't require low latency it is recommended to set the `buffer_size`
passed to :meth:`Synth.start` to a somewhat large value such as `4096` to avoid
glitches.

If you do require low latency response you can decrease the `buffer_size`
argument. A value of `1024` is usually safe for most platforms. Lower values can
be safe but may result in glitches and audio underruns in some situations.
Passing a value of `0` lets PortAudio decide on the buffer size to minimize
latency. This generally works well if the main thread has priority. It may be
too aggressive if other applications are running and interacting with the user.

One thing to note about buffer sizes and latency is that MIDI events that are
scheduled by :class:`Sequencer` can happen at precise positions in the audio
output and will not have any jitter or timing issues. Direct calls to
:class:`Synth` to perform actions can only happen at audio buffer boundaries.
This means that the larger the audio buffer the more timing jitter will happen
for direct calls to :class:`Synth`.

Too Loud / Too Quiet
^^^^^^^^^^^^^^^^^^^^

SoundFonts have many internal settings which control gain and volume. Different
SoundFonts may be adjusted to different expected final sound volumes. If you are
getting sound output that is much too loud or too quiet you should adjust the
gain. You can adjust global gain when constructing the :class:`Synth` object. If
you are loading several SoundFonts you can adjust the relative gain of each one
when calling :meth:`Synth.sfload`. All the gain factors are measured in relative dB.
So a value of `0` means no change, `+3` means double the signal, `-3` means divide
the signal by a factor of 2.
