#
# Python bindings for TinySoundFont
# https://github.com/nwhitehead/tinysoundfont-pybind
#
# Copyright (C) 2024 Nathan Whitehead
#
# This code is licensed under the MIT license (see LICENSE for details)
#

from ._tinysoundfont import MidiMessageType
from ._tinysoundfont import midi_load_memory as _midi_load_memory
from collections import deque
from typing import Callable, Dict, List, Optional
from .synth import Synth

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
        # Event is events as returned by _tinysoundfont.midi_load_memory
        self.events = deque()
        def seq_callback(delta: float) -> float:
            if self.paused:
                return delta
            return self.process(delta)
        self.synth.callback = seq_callback

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
        
        :return: True if there are no more events scheduled for this sequencer (song is over)
        """
        if len(self.events) == 0:
            return True
        if self.events[-1]["t"] < self.time:
            return True
        return False

    def midi_load_memory(self, data: bytes, filter: Optional[Callable[[List[Dict]], Optional[bool]]] = None, persistent: bool = True):
        """Load MIDI data and schedule its events in this sequencer now

        :param data: MIDI data, in Standard MIDI format.
        :param filter: Optional function that takes in individual events and can
            modify them or filter them out.
        :param persistent: Whether to keep events in queue after playing,
            allowing for seeking back to start or arbitrary positions after
            playback has started.

        Filter function should take one input argument, the event, and modify it
        in place as needed. The function should return `None` or `False` to
        indicate to keep the modified event, or `True` to indicate that the
        event should be deleted.
        
        See also: :meth:`midi_load`
        """
        self.data = _midi_load_memory(data)
        events = []
        for event in self.data:
            # Offset by current time of sequencer (MIDI events stored at t=0 are scheduled to start now)
            event["t"] += self.time
            if persistent:
                event["persistent"] = True
            if filter is not None:
                if filter(event) == True:
                    event = None
            # Check for None return value in filtered events, don't add if None
            if event is not None:
                events.append(event)
        events.sort(key=lambda e: e["t"])
        self.events = deque(events)

    def midi_load(self, filename: str, filter: Optional[Callable[[List[Dict]], Optional[bool]]] = None):
        """Load a MIDI file and schedule its events in this sequencer now

        :param filename: Filename to load MIDI data from, in Standard MIDI
            format
        :param filter: Optional function that takes in individual events and can
            modify them or filter them out

        Filter function should take one input argument, the event, and modify it
        in place as needed. The function should return `None` or `False` to
        indicate to keep the modified event, or `True` to indicate that the event
        should be deleted.
        """
        with open(filename, "rb") as fin:
            data = fin.read()
            self.midi_load_memory(data, filter=filter)

    def send(self, event: Dict):
        """Send a single MIDI event to the synth object now, ignoring any time information.
        
        :param event: Single event, with field `type` and `channel` plus any needed additional details for event.

        If the event tries to select a preset that does not exist no error is raised.

        The `type` field is of type :class:`MidiMessageType`.

        For `NOTE_ON`, the event has `key` and `velocity`.

        For `NOTE_OFF`, the event has `key`.

        For `CONTROL_CHANGE`, the event has `control` and `control_value`.

        For `PROGRAM_CHANGE`, the event has `program`.

        For `PITCH_BEND`, the event has `pitch_bend`.
        """
        synth = self.synth
        match event["type"]:
            case MidiMessageType.NOTE_ON:
                synth.noteon(event["channel"], event["key"], event["velocity"])
            case MidiMessageType.NOTE_OFF:
                synth.noteoff(event["channel"], event["key"])
            case MidiMessageType.KEY_PRESSURE:
                # Not handled by TinySoundFont
                pass
            case MidiMessageType.CONTROL_CHANGE:
                synth.control_change(event["channel"], event["control"], event["control_value"])
            case MidiMessageType.PROGRAM_CHANGE:
                try:
                    synth.program_change(event["channel"], event["program"], event["channel"] == 10)
                except Exception:
                    pass
            case MidiMessageType.CHANNEL_PRESSURE:
                # Not handled by TinySoundFont
                pass
            case MidiMessageType.PITCH_BEND:
                synth.pitchbend(event["channel"], event["pitch_bend"])

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
            t = event["t"]
            if t < self.time:
                # Send it if it is not persistent, otherwise ignore
                if "persistent" in event:
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
            if "persistent" in event:
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
