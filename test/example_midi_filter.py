
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("florestan-subset.sfo")

def filter_program_change(event):
    """Make all program changes go to preset 19"""
    match event.action:
        case tinysoundfont.midi.ProgramChange(_program):
            event.action.program = 19 # Church organ

seq = tinysoundfont.Sequencer(synth)
seq.midi_load("1080-c01.mid", filter=filter_program_change)

synth.start(buffer_size=4096)
while not seq.is_empty():
    time.sleep(0.5)
