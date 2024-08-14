import argparse
import sys
import time

from .synth import Synth
from .sequencer import Sequencer


def endswith_any(value, suffixes):
    for suffix in suffixes:
        if value.endswith(suffix):
            return True
    return False


def is_midi(filename):
    return endswith_any(filename, [".mid", ".midi", ".MID", ".MIDI"])


def is_soundfont(filename):
    return endswith_any(filename, [".sf2", ".SF2", ".sf3", ".SF3", ".sfo", ".SFO"])


def main():
    parser = argparse.ArgumentParser(
        prog="tinysoundfont-tool",
        description="Command line tool for examining SoundFonts and MIDI files",
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="Play MIDI file (requires both MIDI and SoundFont files)",
    )
    parser.add_argument("--test", action="store_true", help="Play test SoundFont file")
    parser.add_argument(
        "--info", action="store_true", help="Show information about SoundFont file"
    )
    parser.add_argument(
        "--key",
        type=int,
        action="append",
        default=[],
        help="MIDI key number to play for test (0-127)",
    )
    parser.add_argument(
        "--bank",
        type=int,
        action="append",
        default=[],
        help="MIDI bank number to use for playing test (0-127)",
    )
    parser.add_argument(
        "--preset",
        type=int,
        action="append",
        default=[],
        help="MIDI preset number to use for playing test (0-127)",
    )
    parser.add_argument(
        "--velocity",
        type=int,
        action="append",
        default=[],
        help="MIDI velocity to use for playing test (0-127)",
    )
    parser.add_argument(
        "--drum", action="store_true", help="Set drum mode for play test"
    )
    parser.add_argument(
        "--samplerate",
        type=int,
        default=44100,
        help="Set synthesizer samplerate for playback",
    )
    parser.add_argument(
        "--gain",
        type=float,
        default=0.0,
        help="Set synthesizer global gain for playback",
    )
    parser.add_argument(
        "--buffer_size",
        type=int,
        default=2048,
        help="Set pyaudio buffer size for playback, or 0 for automatic sizing for lowest latency",
    )
    parser.add_argument(
        "filename",
        nargs="+",
        help="SoundFont or MIDI files to use; playing MIDI files requires both MIDI file and SoundFont file",
    )
    args = parser.parse_args()

    midi_filename = None
    soundfont_filename = None
    for filename in args.filename:
        if is_midi(filename):
            midi_filename = filename
        if is_soundfont(filename):
            soundfont_filename = filename

    if args.info:
        if soundfont_filename is None:
            print(
                "No SoundFont file found, a SoundFont file is required for MIDI playback"
            )
            return -2
        print(f"Info for SoundFont {soundfont_filename}")
        synth = Synth(samplerate=args.samplerate, gain=args.gain)
        sfid = synth.sfload(soundfont_filename)
        for bank in range(127):
            for preset in range(127):
                name = synth.sfpreset_name(sfid, bank, preset)
                if name is not None:
                    print(f"{bank} - {preset} : {name}")
        return 0

    if args.test:
        if soundfont_filename is None:
            print(
                "No SoundFont file found, a SoundFont file is required for MIDI playback"
            )
            return -2
        print(f"Testing SoundFont {soundfont_filename}")
        synth = Synth(samplerate=args.samplerate, gain=args.gain)
        sfid = synth.sfload(soundfont_filename)
        if len(args.bank) == 0:
            args.bank.append(0)
        if len(args.preset) == 0:
            args.preset.append(0)
        if len(args.key) == 0:
            args.key.append(60)
        if len(args.velocity) == 0:
            args.velocity.append(100)
        for i in range(16):
            synth.program_select(
                i,
                sfid,
                args.bank[i % len(args.bank)],
                args.preset[i % len(args.preset)],
                is_drums=args.drum,
            )
        for i in range(len(args.key)):
            synth.noteon(
                i, args.key[i % len(args.key)], args.velocity[i % len(args.velocity)]
            )
        synth.start(buffer_size=args.buffer_size)
        time.sleep(3)
        synth.notes_off()
        time.sleep(1)

    if args.play:
        if midi_filename is None:
            print(
                "No MIDI file found, a MIDI file and SoundFont file are required for MIDI playback"
            )
            return -1
        if soundfont_filename is None:
            print(
                "No SoundFont file found, a SoundFont file is required for MIDI playback"
            )
            return -2

        # Let's try to play a MIDI file
        synth = Synth(samplerate=args.samplerate, gain=args.gain)
        sfid = synth.sfload(soundfont_filename)
        seq = Sequencer(synth)
        for i in range(16):
            synth.program_change(i, 0, i == 10)
        seq.midi_load(midi_filename)
        synth.start(buffer_size=args.buffer_size)
        print(f"Playing {midi_filename} with SoundFont {soundfont_filename}")
        while not seq.is_empty():
            time.sleep(0.5)
        time.sleep(1)
        return 0

        return 0

    print("No action to perform, need either --test, --play, or --info")
    return -3


sys.exit(main())
