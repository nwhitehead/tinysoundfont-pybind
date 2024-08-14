#
# Python bindings for TinySoundFont
# https://github.com/nwhitehead/tinysoundfont-pybind
#
# Copyright (C) 2024 Nathan Whitehead
#
# This code is licensed under the MIT license (see LICENSE for details)
#

from .._tinysoundfont import _midi_load_memory
from .._tinysoundfont import MidiMessageType
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


@dataclass
class NoteOn:
    """Action that turns on a single note

    :param key: MIDI note number of note (0-127)
    :param velocity: Velocity of note, 0 means turn off (0-127)
    """

    key: int
    velocity: int = 0


@dataclass
class NoteOff:
    """Action that turns off a single note

    :param key: MIDI note number of note (0-127)
    """

    key: int


@dataclass
class ControlChange:
    """Action that changes a MIDI control value

    :param control: MIDI controller number (0-127)
    :param control_value: Value to change to (0-127)
    """

    control: int
    control_value: int


@dataclass
class ProgramChange:
    """Action that changes current preset program

    :param program: Preset number to use (0-127)
    """

    program: int


@dataclass
class PitchBend:
    """Action that bends pitch of current channel

    :param pitch_bend: How much to bend pitch (0-16383, 8192 means no bend)

    Range of pitch bend is set using RPN
    """

    pitch_bend: int = 8192


Action = NoteOn | NoteOff | ControlChange | ProgramChange | PitchBend


@dataclass
class Event:
    """
    A single event that can be sent to a :class:`Synth` object.

    :param action: Details of what event is
    :param t: Time when event is scheduled, in absolute seconds
    :param channel: Channel to use for event
    :param persistent: Whether to keep event in event list after playing

    """

    action: Action
    t: float = 0
    channel: int = 0
    persistent: bool = True


def event_from_dict(item: Dict) -> Optional[Event]:
    """Convert a dictionary with fields to an Event.

    :param item: Dictionary with fields `t` for time, `type` of type :class:`MidiEventType`, and other fields
    as needed for the event

    :returns: Converted input or `None` if the input could not be converted (unsupported type etc.)
    """
    t = item["t"]
    channel = item["channel"]
    persistent = "persistent" in item and item["persistent"] is not None
    match item["type"]:
        case MidiMessageType.NOTE_ON:
            return Event(
                NoteOn(item["key"], item["velocity"]),
                t=t,
                channel=channel,
                persistent=persistent,
            )
        case MidiMessageType.NOTE_OFF:
            return Event(
                NoteOff(item["key"]), t=t, channel=channel, persistent=persistent
            )
        case MidiMessageType.CONTROL_CHANGE:
            return Event(
                ControlChange(item["control"], item["control_value"]),
                t=t,
                channel=channel,
                persistent=persistent,
            )
        case MidiMessageType.PROGRAM_CHANGE:
            return Event(
                ProgramChange(item["program"]),
                t=t,
                channel=channel,
                persistent=persistent,
            )
        case MidiMessageType.PITCH_BEND:
            return Event(
                PitchBend(item["pitch_bend"]),
                t=t,
                channel=channel,
                persistent=persistent,
            )
        case MidiMessageType.KEY_PRESSURE:
            return None
        case MidiMessageType.CHANNEL_PRESSURE:
            return None


def load_memory(
    data: bytes,
    delta_time: float = 0,
    filter: Optional[Callable[[List[Event]], Optional[bool]]] = None,
    persistent: bool = True,
) -> List[Event]:
    """Load MIDI data and turn into list of events.

    :param data: MIDI data, in Standard MIDI format
    :param delta_time: Time offset to add to all events (default 0)
    :param filter: Optional function that takes in individual events and can
        modify them or filter them out (default None)
    :param persistent: Whether to keep events in queue after playing,
        allowing for seeking back to start or arbitrary positions after
        playback has started (default True)

    :returns: List of events from MIDI data, possibly filtered

    Filter function should take one input argument, the event, and modify it
    in place as needed. The function should return `None` or `False` to
    indicate to keep the modified event, or `True` to indicate that the
    event should be deleted.

    See also: :meth:`load`
    """
    midi_data = _midi_load_memory(data)
    events = []
    for item in midi_data:
        event = event_from_dict(item)
        if event is None:
            continue
        # Offset by time_delta
        event.t += delta_time
        event.persistent = persistent
        if filter is not None:
            if filter(event):
                event = None
        # Check for None return value in filtered events, don't add if None
        if event is not None:
            events.append(event)
    events.sort(key=lambda e: e.t)
    return events


def load(
    filename: str,
    delta_time: float = 0,
    filter: Optional[Callable[[List[Event]], Optional[bool]]] = None,
    persistent: bool = True,
) -> List[Event]:
    """Load MIDI file and turn into list of events.

    :param filename: Filename to load MIDI data from, in Standard MIDI
        format
    :param delta_time: Time offset to add to all events (default 0)
    :param filter: Optional function that takes in individual events and can
        modify them or filter them out (default None)
    :param persistent: Whether to keep events in queue after playing,
        allowing for seeking back to start or arbitrary positions after
        playback has started (default True)

    :returns: List of events from MIDI data, possibly filtered

    Filter function should take one input argument, the event, and modify it
    in place as needed. The function should return `None` or `False` to
    indicate to keep the modified event, or `True` to indicate that the event
    should be deleted.

    See also: :meth:`load_memory`
    """
    with open(filename, "rb") as fin:
        data = fin.read()
        return load_memory(
            data, delta_time=delta_time, filter=filter, persistent=persistent
        )
