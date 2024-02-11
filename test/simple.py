import tinysoundfont
import numpy as np

def test_help():
    import os
    os.environ['PAGER'] = 'cat'
    help(tinysoundfont)

def test_load():
    sf = tinysoundfont.SoundFont('test/example.sf2')
    assert sf.get_preset_count() == 1
    assert sf.get_preset_name(0) == 'El Cheapo Organ'

def test_chord():
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.reset()
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, 0.0)
    sf.note_on(0, 48, 1.0)
    sf.note_on(0, 52, 1.0)
    sf.note_on(0, 55, 1.0)
    samps = 44100
    buffer = np.zeros((samps,), dtype=np.float32)
    sf.render(buffer)
    print(buffer)

    # o = tinysoundfont.SoundFont(i)
    # print(o)
    # o.set_volume(0.5)
    # chan = o.note_on(0, 60, 0.5)
    # print(chan)

def test_all():
    test_help()
    test_load()
    test_chord()

test_all()
