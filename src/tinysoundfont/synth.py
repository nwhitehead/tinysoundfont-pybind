#
# Python bindings for TinySoundFont
# https://github.com/nwhitehead/tinysoundfont-pybind
#
# Copyright (C) 2024 Nathan Whitehead
#
# This code is licensed under the MIT license (see LICENSE for details)
#

from . import _tinysoundfont

from typing import Optional

MAX_CHANNELS = 16


class SoundFontException(Exception):
    """An exception raised from tinysoundfont"""

    pass


class Synth:
    """Create new synthesizer object to control sound generation.

    :param gain: scale factor for audio output, in relative dB (default 0.0)
    :param samplerate: output samplerate in Hz (default 44100)

    If you need to mix many simultaneous voices you may need to turn down the
    `gain` to avoid clipping. Some SoundFonts also require gain adjustment to
    avoid being too loud or too quiet.
    """

    def _get_soundfont(self, sfid):
        if sfid not in self.soundfonts:
            raise SoundFontException("Invalid SoundFont id")
        return self.soundfonts[sfid]

    def _get_sfid(self, chan):
        if chan not in self.channel:
            raise SoundFontException("Invalid channel (channel not assigned)")
        return self.channel[chan]

    def __init__(self, gain: float = 0, samplerate: int = 44100):
        self.p = None
        self.stream = None
        self.gain = gain
        self.samplerate = samplerate
        # soundfonts maps sfid numbers to SoundFont objects
        self.soundfonts = {}
        # Unique identifier creator for this Synth
        self.next_sfid = 0
        # Keep track of which SoundFont to use for different channels
        # Dictionary of channel -> sfid
        self.channel = {}
        # Function to call to perform actions during audio callback
        self.callback = None

    def sfload(
        self, filename_or_bytes: str | bytes, gain: float = 0.0, max_voices: int = 256
    ) -> int:
        """Load SoundFont and return its ID

        :param filename_or_bytes: either a filename containing sf2/sf3/sfo
            SoundFont data or bytes object
        :param gain: gain adjustment for this SoundFont, in relative dB (default
            0.0)
        :param max_voices: maximum number of simultaneous voices (default 256)

        :return: ID of SoundFont to be used by other methods such as
            :func:`program_select`

        When deciding on the value for `max_voices`, one note in a SoundFont may
        use more than one voice. Playing multiple notes also uses more voices.
        If more voices are required than are available, older voices will be cut
        off.

        See also: :meth:`program_select`, :meth:`sfpreset_name`,
        :meth:`sfunload`
        """
        soundfont = _tinysoundfont.SoundFont(filename_or_bytes)
        soundfont.set_output(
            _tinysoundfont.OutputMode.StereoInterleaved,
            self.samplerate,
            self.gain + gain,
        )
        soundfont.set_max_voices(max_voices)
        sfid = self.next_sfid
        self.next_sfid += 1
        self.soundfonts[sfid] = soundfont
        # Set any unassigned channels to use this SoundFont
        for chan in range(MAX_CHANNELS):
            if chan not in self.channel:
                self.channel[chan] = sfid
        return sfid

    def sfunload(self, sfid: int):
        """Unload a SoundFont and free memory it used.

        :param sfid: ID of SoundFont to unload, as returned by :func:`sfload`
        :type sfid: int

        :raises: `SoundFontException` if the SoundFont does not exist

        See also: :meth:`sfload`
        """
        _ = self._get_soundfont(sfid)
        del self.soundfonts[sfid]
        # Clear any channels that refers to this sfid
        self.channel = {
            chan: self.channel[chan]
            for chan in self.channel
            if self.channel[chan] != sfid
        }

    def program_select(
        self, chan: int, sfid: int, bank: int, preset: int, is_drums: bool = False
    ):
        """Select a program from a SoundFont for specific channel

        :param chan: Channel to affect (0-15)
        :param sfid: ID of SoundFont to use
        :param bank: Bank to set (0-127)
        :param preset: Which preset to use (0-127)
        :param is_drums: Whether to set channel to MIDI drum mode (default
            False)

        :raises: `SoundFontException` if the SoundFont does not exist
        :raises: `RuntimeError` if channel, bank, or preset is out of range
        :raises: `RuntimeError` if bank/preset does not match any instrument for
            the SoundFont

        Note that presets are numbered with 0-based indexing. MIDI user
        interfaces typically number presets 1-128.
        """
        soundfont = self._get_soundfont(sfid)
        self.channel[chan] = sfid
        soundfont.channel_set_bank(chan, bank)
        soundfont.channel_set_preset_number(chan, preset, is_drums)

    def program_unset(self, chan: int):
        """Set the preset of a MIDI channel to an unassigned state.

        :param chan: Channel to affect (0-15)

        :raises: `SoundFontException` if channel is out of range
        """
        if chan not in self.channel:
            raise SoundFontException("Invalid channel (channel not assigned)")
        del self.channel[chan]

    def program_change(self, chan: int, preset: int, is_drums: bool = False):
        """Select a program for a specific channel.

        :param chan: Channel to affect (0-15)
        :param preset: Which preset to use (0-127)
        :param is_drums: Whether to set channel to MIDI drum mode (default
            False)

        :raises: `SoundFontException` if channel is out of range or does not
            have a SoundFont loaded
        :raises: `RuntimeError` if bank/preset are out of range or do not match
            any instrument for the SoundFont in the channel

        Note that presets are numbered with 0-based indexing. MIDI user
        interfaces typically number presets 1-128.
        """
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_set_preset_number(chan, preset, is_drums)

    def program_info(self, chan: int) -> (int, int, int):
        """Get SoundFont id, bank, program number, and preset number of channel.

        :param chan: Channel to use (0-15)

        :raises: `SoundFontException` if channel is out of range or has no
            SoundFont loaded

        :return: Tuple containing `(sfid, bank, preset)` indicating SoundFont
            ID, bank number, and preset number
        """
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        bank = soundfont.channel_get_preset_bank(chan)
        preset = soundfont.channel_get_preset_number(chan)
        return (sfid, bank, preset)

    def sfpreset_name(self, sfid: int, bank: int, preset: int) -> Optional[str]:
        """Return name of a SoundFont preset.

        :param sfid: ID of SoundFont to use
        :param bank: Bank to use (0-127)
        :param preset: Which preset to retrieve (0-127)

        :raises: `SoundFontException` if channel is out of range or has no
            SoundFont loaded
        :raises: `RuntimeError` if bank/preset are out of range

        :return: Name of preset in SoundFont, or `None` if preset does not exist
            in SoundFont

        Note that presets are numbered with 0-based indexing. MIDI user
        interfaces typically number presets 1-128.
        """
        soundfont = self._get_soundfont(sfid)
        name = soundfont.get_preset_name(bank, preset)
        if name == "<None>":
            return None
        return name

    def noteon(self, chan: int, key: int, velocity: int) -> bool:
        """Play a note.

        :param chan: Channel to use (0-15)
        :param key: MIDI key to press (0-127), 60 is middle C
        :param velocity: Velocity of keypress (0-127), 0 means to turn off, 127
            is maximum

        :return: `True` if note was valid, `False` if note was outside of legal
            range or channel did not have instrument loaded
        """
        if key < 0 or key > 127:
            return False
        if velocity < 0 or velocity > 127:
            return False
        if chan not in self.channel:
            return False
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_note_on(chan, key, velocity / 127.0)
        return True

    def noteoff(self, chan: int, key: int):
        """Stop a note.

        :param chan: Channel to use (0-15)
        :param key: MIDI key to release (0-127), 60 is middle C

        :return: `True` if note was valid, `False` if note was outside of legal
            range or channel did not have instrument loaded

        It is valid to call `noteoff` on a note that never had `noteon`.
        """
        if key < 0 or key > 127:
            return False
        if chan not in self.channel:
            return False
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_note_off(chan, key)
        return True

    def notes_off(self, chan: Optional[int] = None):
        """Turn off all playing notes in all channels or one specific channel.

        :param chan: Channel to use (0-15) or None to indicate all channels

        Some instruments have long decays or may continue to produce sound after
        a NOTE_OFF event. If you need all sounds to stop playing use
        :meth:`sounds_off`.
        """
        if chan is None:
            for chan in range(16):
                self.control_change(chan, 123, 0)
        else:
            self.control_change(chan, 123, 0)

    def sounds_off(self, chan: Optional[int] = None):
        """Turn off all playing sounds in all channels or one specific channel.

        :param chan: Channel to use (0-15) or None to indicate all channels

        Some instruments have long decays or may continue to produce sound after
        a NOTE_OFF event. If you need all notes to stop playing and continue
        producing the decay, use :meth:`notes_off`.
        """
        if chan is None:
            for chan in range(16):
                self.control_change(chan, 120, 0)
        else:
            self.control_change(chan, 120, 0)

    def control_change(self, chan: int, controller: int, control_value: int):
        """Change control value for a specific channel.

        :param chan: Channel to use (0-15)
        :param controller: Controller to update, (0-127), meaning defined by
            MIDI 1.0 standard
        :param control_value: Value to use for update, (0-127)

        The interpretation of controller number is from the MIDI 1.0 standard.
        Supported controller values that have an effect are:

        .. include:: table_supported_controller.rstinc

        The supported Registered Parameter Names (RPN) are:

        .. include:: table_supported_rpn.rstinc

        .. include:: note_rpn.rstinc
        """
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_midi_control(chan, controller, control_value)

    def set_tuning(self, chan: int, tuning: float):
        """Set tuning for a channel.

        :param chan: Channel to affect (0-15)
        :param tuning: Tuning adjustment in semitones (default 0.0)
        """
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_set_tuning(chan, tuning)

    def pitchbend(self, chan: int, value: int):
        """Set pitch wheel position for a channel.

        :param chan: Channel to affect (0-15)
        :param value: Value from 0 to 16383 indicating pitch bend down to pitch
            bend up (default 8192, no pitch change)

        See also: :meth:`pitchbend_range`
        """
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_set_pitch_wheel(chan, value)

    def pitchbend_range(self, chan: int, semitones: float):
        """Set pitch bend range up and down for a channel.

        :param chan: Channel to affect (0-15)
        :param semitones: Pitch bend range up and down in semitones (default
            2.0)

        See also: :meth:`pitchbend`
        """
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_set_pitch_range(chan, semitones)

    def start(self, buffer_size: int = 1024, **kwargs):
        """Start audio playback in a separate thread.

        :param buffer_size: Number of samples to buffer or 0 for automatic
            sizing for low latency (default 1024)

        Extra keyword arguments will be passed to the `pyaudio` stream
        constructor. Useful arguments might include:

        * `output_device_index` -- index of output device to use, or `None` for
          default output device

        Note that depending on your platform `pyaudio` may recognize a large
        number of devices not all of which are suitable for audio playback. You
        may need to use `pyaudio` method `get_host_api_info_by_index()` to find
        details about the `pyaudio` devices and choose a suitable index.

        The separate audio playback thread will continue generating and playing
        samples until stopped with :meth:`stop`.

        The audio thread will not prevent the main thread from exiting. If you
        turn on notes and call :meth:`start`, your main thread will need to call
        :func:`time.sleep` to let time pass to be able to hear the notes
        playing. To schedule note events through time see :class:`Sequencer`.

        See also: :meth:`stop`
        """

        # Import pyaudio here so if this function is not used there is no dependency
        import pyaudio

        def callback(in_data, frame_count, time_info, status):
            buffer = self.generate(samples=frame_count)
            # PyAudio needs actual bytes, not just memoryview
            return (bytes(buffer), pyaudio.paContinue)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=2,
            rate=self.samplerate,
            output=True,
            stream_callback=callback,
            frames_per_buffer=buffer_size,
            **kwargs
        )

    def stop(self):
        """Stop audio playback thread.

        See also: :meth:`start`
        """
        if self.p is not None and self.stream is not None:
            self.stream.close()
            self.p.terminate()

    def generate(self, samples: int, buffer: Optional[memoryview] = None) -> memoryview:
        """Generate fixed number of output samples.

        :param samples: Number of samples to generate
        :param buffer: Existing buffer to fill, or `None` to allocate new buffer

        :returns: View into buffer with samples filled in stereo float32 format.

        This method fills in a fixed number of output samples in the output
        buffer given (or creates a new buffer if none is given). The sequencer
        callback is called as needed to trigger MIDI events at the correct
        sample location.
        """
        CHANNELS = 2
        SIZEOF_FLOAT_IN_BYTES = 4
        if buffer is None:
            # Wrap with `memoryview` so slicing is references inside the buffer, not copies
            buffer = memoryview(bytearray(samples * CHANNELS * SIZEOF_FLOAT_IN_BYTES))
        generated = 0
        while generated < samples:
            delta = (samples - generated) / self.samplerate
            # Call all the relevant callbacks, which each may shorten delta
            # Each callback does any actions it needs to do that are currently scheduled, then returns how much delta can advance
            if self.callback is not None:
                delta = min(self.callback(delta), delta)
            # Compute actual frame count to render based on return value in seconds (round up to keep making progress in each iteration)
            actual_frame_count = int(delta * self.samplerate + 0.999)
            # Index into buffer at frame boundaries
            pos = generated * CHANNELS * SIZEOF_FLOAT_IN_BYTES
            sz_bytes = actual_frame_count * CHANNELS * SIZEOF_FLOAT_IN_BYTES
            self.generate_simple(actual_frame_count, buffer=buffer[pos : pos + sz_bytes])
            generated += actual_frame_count
        return buffer

    def generate_simple(self, samples: int, buffer: Optional[memoryview] = None) -> memoryview:
        """Generate fixed number of output samples, ignoring sequenced events.

        :param samples: Number of samples to generate
        :param buffer: Existing buffer to fill, or `None` to allocate new buffer

        :returns: View into buffer with samples filled in stereo float32 format.

        This method fills in a fixed number of output samples in the output
        buffer given (or creates a new buffer if none is given). The sequencer
        is not called from this method so no new events are ever triggered by
        this method.

        See also: :meth:`generate`
        """
        CHANNELS = 2
        SIZEOF_FLOAT_IN_BYTES = 4
        if buffer is None:
            buffer = memoryview(bytearray(samples * CHANNELS * SIZEOF_FLOAT_IN_BYTES))
        mix = False
        for soundfont in self.soundfonts.values():
            soundfont.render(buffer, mix)
            # After first render turn on mix to mix together all sounds
            mix = True
        return buffer
