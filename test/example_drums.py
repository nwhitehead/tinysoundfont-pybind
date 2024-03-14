
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("FluidR3_GM.sf2")
synth.program_select(0, sfid, 0, 0, True)

seq = tinysoundfont.Sequencer(synth)
seq.midi_load("drum.mid")
synth.start(buffer_size=4096)

while not seq.is_empty():
    time.sleep(0.5)
time.sleep(2.0)
