
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("florestan-piano.sf2")
synth.program_select(0, sfid, 0, 0)
synth.start()
synth.noteon(0, 48, 100)
time.sleep(1.0)
