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
        # events stores events for future, ordered by time
        # Queue has items (t, event)
        # Event is events as returned by _tinysoundfont.midi_load_memory
        self.events = deque()
        self.synth.callback = lambda delta: self.process(delta)

    def midi_load_memory(self, data: bytes, filter: Optional[Callable[[List[Dict]], Optional[bool]]] = None):
        """Load MIDI data and schedule its events in this sequencer now

        :param data: MIDI data, in Standard MIDI format
        :param filter: Optional function that takes in individual events and can
            modify them or filter them out

        Filter function should take one input argument, the event, and modify it
        in place as needed. The function should return `None` or `False` to
        indicate to use the modified event, or `True` to indicate that the event
        should be deleted.
        
        See also: :meth:`midi_load`
        """
        self.data = _midi_load_memory(data)
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

    def midi_load(self, filename: str, filter: Optional[Callable[[List[Dict]], Optional[bool]]] = None):
        """Load a MIDI file and schedule its events in this sequencer now

        :param filename: Filename to load MIDI data from, in Standard MIDI
            format
        :param filter: Optional function that takes in individual events and can
            modify them or filter them out

        Filter function should take one input argument, the event, and modify it
        in place as needed. The function should return `None` or `False` to
        indicate to use the modified event, or `True` to indicate that the event
        should be deleted.
        """
        with open(filename, "rb") as fin:
            data = fin.read()
            self.midi_load_memory(data, filter=filter)

    def send(self, event: Dict):
        """Send a single MIDI event to the synth object now, ignoring any time information.
        
        :param event: Single event, with fields `t` and `type` plus any needed additional details for event.
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
                synth.program_change(event["channel"], event["program"])
            case MidiMessageType.CHANNEL_PRESSURE:
                # Not handled by TinySoundFont
                pass
            case MidiMessageType.PITCH_BEND:
                synth.pitchbend(event["channel"], event["pitch_bend"])

    def process(self, delta: float) -> float:
        """Send any events that need to be sent now.

        :param delta: How many seconds to advance time.
        :returns: How far time was actually advanced (may be smaller than `delta`).

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
            self.send(event)
        # If we get here that means events are done
        # Advance full time
        self.time += delta
        return delta
