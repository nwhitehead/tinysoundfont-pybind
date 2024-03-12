
import tinysoundfont
import time


synth = tinysoundfont.Synth(samplerate=22050, gain=-3.0)
# Try with buffer size large enough that listener will hear jitter if notes must start/end on buffer boundaries
synth.start(buffer_size=4096)

sfid = synth.sfload("test/example.sf2", gain=-12.0)
assert sfid == 0
sfid2 = synth.sfload("test/florestan-subset.sfo", gain=-1.0)
assert sfid2 == 1
name = synth.sfpreset_name(sfid, 0, 0)
assert name == "El Cheapo Organ"
name = synth.sfpreset_name(sfid2, 0, 2)
assert name == "Piano"
synth.program_select(0, sfid, 0, 0)
info = synth.program_info(0)
assert info == (0, 0, 0)
synth.program_select(1, sfid2, 0, 2)

synth.noteon(0, 48, 100)
synth.noteon(1, 60, 100)
synth.noteon(1, 64, 100)
synth.noteon(1, 67, 100)
time.sleep(0.5)
# Tune channel 0 up half a semitone
synth.set_tuning(0, 0.5)
time.sleep(0.5)
synth.noteoff(0, 48)
synth.noteoff(1, 60)
synth.noteoff(1, 64)
synth.noteoff(1, 67)
time.sleep(1.0)

synth.sfunload(sfid)
synth.sfunload(sfid2)
sfid2 = synth.sfload("test/florestan-subset.sfo", gain=-1.0)
for bank in range(127):
    for i in range(127):
        name = synth.sfpreset_name(sfid2, bank, i)
        if name:
            print(bank, i, name)

def filter_program_change(event):
    """Make all program changes go to preset 40 (violin)"""
    if event["type"] == tinysoundfont.MidiMessageType.PROGRAM_CHANGE:
        event["program"] = 40
seq = tinysoundfont.Sequencer(synth)
seq.midi_load("test/1080-c01.mid", filter=filter_program_change)
time.sleep(10)

with pytest.raises(Exception):
    synth.sfunload(sfid)
synth.sfunload(sfid2)
synth.stop()

