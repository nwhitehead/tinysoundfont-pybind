
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("test/FluidR3_GM.sf2", gain=-6.0)
synth.program_select(0, sfid, 0, 8) # Celesta
synth.program_select(1, sfid, 0, 15) # Dulcimer
synth.program_select(2, sfid, 0, 24) # Nylon String Guitar
synth.start()

time.sleep(0.5)
synth.noteon(0, 60, 100)
synth.noteon(0, 67, 100)
time.sleep(0.5)
synth.noteon(1, 60, 100)
time.sleep(0.5)
synth.noteon(2, 70, 75)
time.sleep(0.5 / 8)
synth.noteoff(2, 70)
synth.noteon(2, 67, 75)

time.sleep(1.0)