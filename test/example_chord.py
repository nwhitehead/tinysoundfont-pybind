
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("florestan-piano.sf2")
synth.program_select(0, sfid, 0, 0)
synth.start()

time.sleep(0.5)

synth.noteon(0, 48, 100)
synth.noteon(0, 52, 100)
synth.noteon(0, 55, 100)

time.sleep(0.5)

synth.noteoff(0, 48)
synth.noteoff(0, 52)
synth.noteoff(0, 55)

time.sleep(0.5)
