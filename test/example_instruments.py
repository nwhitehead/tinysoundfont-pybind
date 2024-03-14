
import tinysoundfont
import time

synth = tinysoundfont.Synth()
sfid = synth.sfload("florestan-subset.sfo")
synth.program_select(0, sfid, 0, 12) # Marimba
synth.program_select(1, sfid, 0, 45) # PizzicatoStr
synth.program_select(2, sfid, 0, 24) # Nylon-str.Gt
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
synth.noteoff(0, 60)
synth.noteoff(0, 67)
synth.noteoff(1, 60)
synth.noteoff(2, 67)

time.sleep(1.0)
