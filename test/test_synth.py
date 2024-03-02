import pytest
import tinysoundfont
import time


def test_0():
    assert int(tinysoundfont.MidiMessageType.NOTE_ON) == 0x90

    with open("test/1080-c01.mid", "rb") as fin:
        contents = fin.read()
        data = tinysoundfont.midi_load_memory(contents)
        assert len(data) == 1852
        assert data[0] == {
            "t": 0.0,
            "type": tinysoundfont.MidiMessageType.SET_TEMPO,
            "channel": 7,
            "bpm": 115.00002875000719,
        }
        assert data[4] == {
            "t": 0.0,
            "type": tinysoundfont.MidiMessageType.PROGRAM_CHANGE,
            "channel": 1,
            "program": 40,
            "bpm": 115.00002875000719,
        }
        assert data[7] == {
            "t": 0.0,
            "type": tinysoundfont.MidiMessageType.NOTE_ON,
            "channel": 1,
            "key": 62,
            "velocity": 100,
            "bpm": 115.00002875000719,
        }

    synth = tinysoundfont.Synth(samplerate=22050, gain=-3.0)

    seq = tinysoundfont.Sequencer()
    seq.midi_load("test/1080-c01.mid")
    print(seq.data)

    synth.start()

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
    time.sleep(1.0)
    synth.noteoff(0, 48)
    synth.noteoff(1, 60)
    synth.noteoff(1, 64)
    synth.noteoff(1, 67)
    time.sleep(0.5)

    synth.sfunload(sfid)
    with pytest.raises(Exception):
        synth.sfunload(sfid)
    synth.sfunload(sfid2)
    synth.stop()


if __name__ == "__main__":
    test_0()
