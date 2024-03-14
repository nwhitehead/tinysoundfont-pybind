
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("FluidR3_GM.sf2")

seq = tinysoundfont.Sequencer(synth)
seq.midi_load("1080-c01.mid")

# Larger buffer because latency is not important
synth.start(buffer_size=4096)

while not seq.is_empty():
    time.sleep(0.5)
