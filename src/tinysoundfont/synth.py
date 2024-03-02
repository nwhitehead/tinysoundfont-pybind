from . import _tinysoundfont
from ._tinysoundfont import MidiMessageType, midi_load_memory

from collections import deque

# Drum channels have separate samples per key
DRUM_CHANNEL = 10


class SoundFontException(Exception):
    pass


class Sequencer:
    """A Sequencer schedules MIDI events over time"""
    def __init__(self):
        self.time = 0.0
        # events stores events for future, ordered by time
        # Queue has items (t, event)
        # Event is events as returned by _tinysoundfont.midi_load_memory
        self.events = deque()
    def midi_load(self, filename, filter=None):
        """Load a MIDI file and schedule its events in this sequencer now
        
        Keyword arguments:
        
        filter -- Optional function that takes in individual events.

        Filter function should take one input argument, the event, and modify it
        in place. The function should return None to indicate to use the
        modified event, or True to indicate that the event should be deleted.
        """
        with open(filename, "rb") as fin:
            data = fin.read()
            self.data = _tinysoundfont.midi_load_memory(data)
            events = []
            for event in self.data:
                # Offset by current time of sequencer (MIDI events stored at t=0 are scheduled to start now)
                event["t"] += self.time
                if filter is not None:
                    if filter(event) == True:
                        event = None
                # Check for None return value in filtered events, don't add if None
                if event is not None:
                    events.append(event)
            events.sort(key=lambda e: e["t"])
            self.events = deque(events)
    def perform(self, event, synth):
        """Send a MIDI event to the synth object now (ignore time information)"""
        match event["type"]:
            case MidiMessageType.NOTE_ON:
                synth.noteon(event["channel"], event["key"], event["velocity"])
            case MidiMessageType.NOTE_OFF:
                synth.noteoff(event["channel"], event["key"])
            case MidiMessageType.PROGRAM_CHANGE:
                synth.program_change(event["channel"], event["program"])
            case MidiMessageType.CONTROL_CHANGE:
                synth.control_change(event["channel"], event["control"], event["control_value"])

    def process(self, delta, synth):
        """Process delta seconds sending events to synth

        Return actual delta that can be generated before more events need to be processed.
        Returned value will always be between 0 and delta.
        """
        # Send all events that are scheduled for time <= self.time
        while len(self.events) > 0:
            # Look at earliest event in deque
            event = self.events[0]
            t = event["t"]
            if t > self.time:
                # Don't do event yet or remove it, need to wait until its time
                true_delta = min(delta, t - self.time)
                self.time += true_delta
                return true_delta
            # Head event should actually be done, so remove it
            event = self.events.popleft()
            # Now do it
            self.perform(event, synth)
        # If we get here that means events ran dry
        # Advance full time
        self.time += delta
        return delta


class Synth:
    """Synth represents a synthesizer that can load a SoundFont and produce audio"""

    def _get_soundfont(self, sfid):
        if sfid not in self.soundfonts:
            raise SoundFontException("Invalid SoundFont id")
        return self.soundfonts[sfid]

    def _get_sfid(self, chan):
        if chan not in self.channel:
            raise SoundFontException("Invalid channel (channel not assigned)")
        return self.channel[chan]

    def __init__(self, gain=0, samplerate=44100, buffer_size=0):
        """Create new synthesizer object to control sound generation

        Keyword arguments:
        gain -- scale factor for audio output in relative dB (default 0.0)
        samplerate -- output samplerate in Hz (default 44100)
        buffer_size -- number of samples to buffer or 0 for automatic sizing for low latency (default 0)

        If you need to mix many simultaneous voices you may need to turn down
        the gain to avoid clipping. Some SoundFonts also require gain adjustment
        to avoid being too loud or too quiet.
        """
        self.p = None
        self.stream = None
        self.gain = gain
        self.samplerate = samplerate
        self.buffer_size = buffer_size
        # soundfonts maps sfid numbers to SoundFont objects
        self.soundfonts = {}
        # Unique identifier creator for this Synth
        self.next_sfid = 0
        # Keep track of which SoundFont to use for different channels
        # Dictionary of channel -> sfid
        self.channel = {}
        # Keep track of scheduled MIDI events for callback
        self.sequencer = Sequencer()

    def sfload(self, filename, gain=0.0, max_voices=256):
        """Load SoundFont and return its ID

        Arguments:
        filename -- filename containing sf2/sf3/sfo SoundFont data, or `bytes` data directly

        Keyword arguments:
        gain -- gain adjustment for this SoundFont in relative dB (default 0.0)
        max_voices -- maximum number of simultaneous voices (default 256)

        Returns ID of SoundFont to be used by other methods such as `program_select`.
        One note in a SoundFont may use more than one voice. Playing multiple notes
        also uses more voices. If more voices are required than are available, older
        voices will be cut off.
        """
        soundfont = _tinysoundfont.SoundFont(filename)
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
        for chan in range(16):
            if chan not in self.channel:
                self.channel[chan] = sfid
        return sfid

    def sfunload(self, sfid):
        """Unload a SoundFont and free memory it used"""
        _ = self._get_soundfont(sfid)
        del self.soundfonts[sfid]
        # Clear any channels that refers to this sfid
        self.channel = {
            chan: self.channel[chan]
            for chan in self.channel
            if self.channel[chan] != sfid
        }

    def program_select(self, chan, sfid, bank, preset):
        """Select a program for specific channel"""
        soundfont = self._get_soundfont(sfid)
        self.channel[chan] = sfid
        soundfont.channel_set_bank(chan, bank)
        soundfont.channel_set_preset_number(chan, preset, chan == DRUM_CHANNEL)

    def program_unset(self, chan):
        """Set the preset of a MIDI channel to an unassigned state"""
        if chan not in self.channel:
            raise SoundFontException("Invalid channel (channel not assigned)")
        del self.channel[chan]

    def program_change(self, chan, preset):
        """Select a program for a specific channel that already has a SoundFont assigned"""
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_set_preset_number(chan, preset, chan == DRUM_CHANNEL)

    def program_info(self, chan):
        """Get SoundFont id, bank, program number, and preset name of channel"""
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        bank = soundfont.channel_get_preset_bank(chan)
        preset = soundfont.channel_get_preset_number(chan)
        return (sfid, bank, preset)

    def sfpreset_name(self, sfid, bank, number):
        """Return name of a SoundFont preset"""
        soundfont = self._get_soundfont(sfid)
        return soundfont.get_preset_name(bank, number)

    def noteon(self, chan, key, vel):
        """Play a note"""
        if key < 0 or key > 127:
            return False
        if vel < 0 or vel > 127:
            return False
        if chan not in self.channel:
            return False
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_note_on(chan, key, vel / 127.0)
        return True

    def noteoff(self, chan, key):
        """Stop a note"""
        if key < 0 or key > 127:
            return False
        if chan not in self.channel:
            return False
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_note_off(chan, key)
        return True

    def control_change(self, chan, controller, control_value):
        """Change control value for a specific channel"""
        sfid = self._get_sfid(chan)
        soundfont = self._get_soundfont(sfid)
        soundfont.channel_midi_control(chan, controller, control_value)

    def start(self, driver=None):
        """Start audio playback"""
        # Import pyaudio here so if this function is not used there is no dependency
        import pyaudio

        def callback(in_data, frame_count, time_info, status):
            CHANNELS = 2
            SIZEOF_FLOAT_IN_BYTES = 4
            # Wrap with `memoryview` so slicing is references inside the buffer, not copies
            buffer = memoryview(bytearray(frame_count * CHANNELS * SIZEOF_FLOAT_IN_BYTES))            
            generated = 0
            while generated < frame_count:
                delta = (frame_count - generated) / self.samplerate
                delta = self.sequencer.process(delta, self)
                # Compute actual frame count to render based on return value in seconds (round up to keep making progress)
                actual_frame_count = int(delta * self.samplerate + 0.999)
                # Index into buffer at frame boundaries
                pos = generated * CHANNELS * SIZEOF_FLOAT_IN_BYTES
                sz_bytes = actual_frame_count * CHANNELS * SIZEOF_FLOAT_IN_BYTES
                self.generate(actual_frame_count, buffer=buffer[pos:pos+sz_bytes])
                generated += actual_frame_count
            return (bytes(buffer), pyaudio.paContinue)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=2,
            rate=self.samplerate,
            output=True,
            stream_callback=callback,
            frames_per_buffer=self.buffer_size,
        )

    def stop(self):
        """Stop audio playback"""
        if self.p is not None and self.stream is not None:
            self.stream.close()
            self.p.terminate()

    def generate(self, samples, buffer=None):
        """Generate fixed number of output samples in stereo float32 format as bytearray"""
        CHANNELS = 2
        SIZEOF_FLOAT_IN_BYTES = 4
        if buffer is None:
            buffer = bytearray(samples * CHANNELS * SIZEOF_FLOAT_IN_BYTES)
        mix = False
        for soundfont in self.soundfonts.values():
            soundfont.render(buffer, mix)
            # After first render turn on mix to mix together all sounds
            mix = True
        return buffer

