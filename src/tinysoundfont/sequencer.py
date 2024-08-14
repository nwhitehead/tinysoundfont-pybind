#
# Python bindings for TinySoundFont
# https://github.com/nwhitehead/tinysoundfont-pybind
#
# Copyright (C) 2024 Nathan Whitehead
#
# This code is licensed under the MIT license (see LICENSE for details)
#

from collections import deque
from typing import List
from .synth import Synth
from .midi import (
    load,
    Event,
    NoteOn,
    NoteOff,
    ControlChange,
    ProgramChange,
    PitchBend,
)

DRUM_CHANNEL = 9

class Sequencer:
    """A Sequencer schedules MIDI events over time.

    :param synth: The synthesizer object to send events to.
    """

    def __init__(self, synth: Synth):
        self.synth = synth
        self.time = 0.0
        self.paused = False
        # events stores events for future, ordered by time
        # Queue has items (t, event)
        self.events = deque()

        def seq_callback(delta: float) -> float:
            if self.paused:
                return delta
            return self.process(delta)

        self.synth.callback = seq_callback

    def add(self, events: List[Event]):
        """Add a list of MIDI events to queue for sending.

        :param events: List of MIDI events

        See :func:`midi.load` for generating the list of events.
        See :func:`midi_load` for directly loading a MIDI file.
        """
        self.events.extend(events)

    def midi_load(self, filename: str, **kwargs):
        """Load MIDI file and schedule events.

        :param filename: Filename to load MIDI data from, in Standard MIDI
            format

        Any additional keyword arguments are passed to :func:`midi.load`. See
        :func:`midi.load` for documentation on additional keyword arguments.
        """
        events = load(filename, **kwargs)
        self.add(events)

    def get_time(self) -> float:
        """Get current playing time of sequencer.

        :return: current playing time of sequencer in seconds of absolute time since sequencer started
        """
        return self.time

    def set_time(self, time: float):
        """Set current playing time of sequencer.

        :param time: New absolute time in seconds

        Note that if previously scheduled events did not have `persistent` set
        then the events will no longer exist and will not play again.

        Note that MIDI expects events to happen in sequence. So if there is a
        program change as an event and you set the time to before that event,
        you might get the new instrument at a position where the previous
        instrument should have played. In general seeking back to the start of
        the MIDI events should work. Other random seeking may have unintended
        effects.

        To avoid stuck notes, this method turns off all keypresses using
        :meth:`notes_off`. It does not stop all sounds so playing notes may
        still have time to decay. If needed you can call :meth:`sounds_off`
        to stop all playing sounds immediately.
        """
        self.time = time
        self.notes_off()

    def pause(self, pause_value=True):
        """Pause or unpause playback.

        When playback is paused, time does not advance. No new events will be
        sent to the :class:`Synth` object connected to the sequencer. If notes
        are playing, they will continue to play.

        To prevent notes from continuing to play during pause, this method calls
        :meth:`notes_off`. You may want to call :meth:`sound_off` to stop all
        sound playing immediately if needed.
        """
        self.paused = pause_value
        self.notes_off()

    def notes_off(self):
        """Send NOTE_OFF for all currently playing notes of the Synth object."""
        self.synth.notes_off()

    def sounds_off(self):
        """Turn off all sounds of the Synth object."""
        self.synth.sounds_off()

    def is_empty(self) -> bool:
        """Return True if there are no more events scheduled.

        :return: True if there are no more events scheduled for this sequencer
            (song is over)

        Songs often end on a final NOTEOFF event that may have a decay time. It
        is often good to wait some amount of time before looping or scheduling a
        new song.
        """
        if len(self.events) == 0:
            return True
        if self.events[-1].t < self.time:
            return True
        return False

    def send(self, event: Event):
        """Send a single MIDI event to the synth object now, ignoring any time information.

        :param event: Single event to send

        If the event tries to select a preset that does not exist no error is raised.

        """
        synth = self.synth
        channel = event.channel
        match event.action:
            case NoteOn(key, velocity):
                synth.noteon(channel, key, velocity)
            case NoteOff(key):
                synth.noteoff(channel, key)
            case ControlChange(control, control_value):
                synth.control_change(channel, control, control_value)
            case ProgramChange(program):
                try:
                    synth.program_change(channel, program, channel == DRUM_CHANNEL)
                except Exception:
                    pass
            case PitchBend(pitch_bend):
                synth.pitchbend(channel, pitch_bend)

    def process(self, delta: float) -> float:
        """Advance time and send any events that need to be sent to the Synth.

        :param delta: How many seconds to advance time
        :returns: How far time was actually advanced (may be smaller than `delta`)

        """
        # Need to send all events with time <= self.time if not persistent
        # Persistent events only send events with time == self.time
        pos = 0
        while pos < len(self.events):
            # Look at earliest event in deque
            event = self.events[pos]
            t = event.t
            if t < self.time:
                # Send it if it is not persistent, otherwise ignore
                if event.persistent:
                    pos += 1
                else:
                    self.events.popleft()
                    self.send(event)
                continue
            if t > self.time:
                # Don't do event yet or remove it, need to wait until its time
                true_delta = min(delta, t - self.time)
                self.time += true_delta
                return true_delta
            # If we get here, t == self.time
            # Head event needs to be done
            if event.persistent:
                pos += 1
            else:
                self.events.popleft()
                # Don't change pos here, the popleft shifts pos to be next event
            # Now do it
            self.send(event)
        # If we get here that means events are done
        # Advance full time
        self.time += delta
        return delta
