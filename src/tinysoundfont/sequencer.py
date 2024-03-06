#
# Python bindings for TinySoundFont
# https://github.com/nwhitehead/tinysoundfont-pybind
#
# Copyright (C) 2024 Nathan Whitehead
#
# This code is licensed under the MIT license (see LICENSE for details)
#

from ._tinysoundfont import MidiMessageType, midi_load_memory
from collections import deque

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
            self.data = midi_load_memory(data)
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
