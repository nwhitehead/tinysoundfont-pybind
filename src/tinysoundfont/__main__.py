
import argparse
import sys
import time

from .synth import Synth, SoundFontException
from .sequencer import Sequencer, MidiMessageType

def endswith_any(value, suffixes):
    for suffix in suffixes:
        if value.endswith(suffix):
            return True
    return False

def is_midi(filename):
    return endswith_any(filename, ['.mid', '.midi', '.MID', '.MIDI'])

def is_soundfont(filename):
    return endswith_any(filename, ['.sf2', '.SF2', '.sf3', '.SF3', '.sfo', '.SFO'])

def main():
    parser = argparse.ArgumentParser(
        prog='tinysoundfont-tool',
        description='Command line tool for examining SoundFonts and MIDI files')
    parser.add_argument('--play', action='store_true', help='Play MIDI file (requires both MIDI and SoundFont files)')
    parser.add_argument('--test', action='store_true', help='Play test SoundFont file')
    parser.add_argument('--key', type=int, action='append', default=[], help='MIDI key number to play for test (0-127)')
    parser.add_argument('--bank', type=int, action='append', default=[], help='MIDI bank number to use for playing test (0-127)')
    parser.add_argument('--preset', type=int, action='append', default=[], help='MIDI preset number to use for playing test (0-127)')
    parser.add_argument('--velocity', type=int, action='append', default=[], help='MIDI velocity to use for playing test (0-127)')
    parser.add_argument('--drum', action='store_true', help='Set drum mode for play test')
    parser.add_argument('--samplerate', type=int, default=44100, help='Set synthesizer samplerate for playback')
    parser.add_argument('--gain', type=float, default=0.0, help='Set synthesizer global gain for playback')
    parser.add_argument('--buffer_size', type=int, default=2048, help='Set pyaudio buffer size for playback, or 0 for automatic sizing for lowest latency')
    parser.add_argument('filename', nargs='+', help='SoundFont or MIDI files to use; playing MIDI files requires both MIDI file and SoundFont file')
    args = parser.parse_args()

    if args.play:
        midi_filename = None
        soundfont_filename = None
        for filename in args.filename:
            if is_midi(filename):
                midi_filename = filename
            if is_soundfont(filename):
                soundfont_filename = filename
        if midi_filename is None:
            print('No MIDI file found, a MIDI file and SoundFont file are required for MIDI playback')
            return -1
        if soundfont_filename is None:
            print('No SoundFont file found, a SoundFont file is required for MIDI playback')
            return -2

        # Let's try to play a MIDI file
        synth = Synth(samplerate=args.samplerate, gain=args.gain)
        sfid = synth.sfload(soundfont_filename)
        seq = Sequencer(synth)
        seq.midi_load(midi_filename)
        synth.start(buffer_size=args.buffer_size)        
        print(f'Playing {midi_filename} with SoundFont {soundfont_filename}')
        while not seq.is_empty():
            time.sleep(0.5)
        time.sleep(1)
    if args.test:
        print('test')

sys.exit(main())