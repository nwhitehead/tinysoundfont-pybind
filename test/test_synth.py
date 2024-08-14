import pytest
import tinysoundfont
import time


def test_0():
    assert int(tinysoundfont.midi.MidiMessageType.NOTE_ON) == 0x90

    with open("test/1080-c01.mid", "rb") as fin:
        contents = fin.read()
        data = tinysoundfont.midi._midi_load_memory(contents)
        assert len(data) == 1852
        assert data[0] == {
            "t": 0.0,
            "type": tinysoundfont.midi.MidiMessageType.SET_TEMPO,
            "channel": 7,
            "bpm": 115.00002875000719,
        }
        assert data[4] == {
            "t": 0.0,
            "type": tinysoundfont.midi.MidiMessageType.PROGRAM_CHANGE,
            "channel": 1,
            "program": 40,
            "bpm": 115.00002875000719,
        }
        assert data[7] == {
            "t": 0.0,
            "type": tinysoundfont.midi.MidiMessageType.NOTE_ON,
            "channel": 1,
            "key": 62,
            "velocity": 100,
            "bpm": 115.00002875000719,
        }

    synth = tinysoundfont.Synth(samplerate=22050, gain=-3.0)
    # Try with buffer size large enough that listener will hear jitter if notes must start/end on buffer boundaries
    synth.start(buffer_size=4096)

    sfid = synth.sfload("test/florestan-piano.sf2", gain=-12.0)
    assert sfid == 0
    sfid2 = synth.sfload("test/florestan-subset.sfo", gain=-1.0)
    assert sfid2 == 1
    name = synth.sfpreset_name(sfid, 0, 0)
    assert name == "Piano"
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
        match event.action:
            case tinysoundfont.midi.ProgramChange(_program):
                event.program = 40
    seq = tinysoundfont.Sequencer(synth)
    seq.midi_load("test/1080-c01.mid", filter=filter_program_change)
    time.sleep(10)

    with pytest.raises(Exception):
        synth.sfunload(sfid)
    synth.sfunload(sfid2)
    synth.stop()

def test_midi_generate():
    import numpy as np

    synth = tinysoundfont.Synth()
    _sfid = synth.sfload("test/florestan-subset.sfo")

    seq = tinysoundfont.Sequencer(synth)
    seq.midi_load("test/1080-c01.mid")

    # Generate 1 second buffer
    buffer = synth.generate(44100)
    block = np.frombuffer(bytes(buffer), dtype=np.float32)
    assert block.min() < block.max()
