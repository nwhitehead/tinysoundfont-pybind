
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("test/FluidR3_GM.sf2", gain=-3.0)

seq = tinysoundfont.Sequencer(synth)
seq.midi_load("test/1080-c01.mid")

# Larger buffer because latency is not important
synth.start(buffer_size=4096)

while not seq.is_empty():
    time.sleep(0.5)
