import tinysoundfont
import numpy as np
import scipy.io.wavfile

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
    sf.set_max_voices(8)
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.set_channel_preset_index(0, 0)
    sf.set_channel_preset_index(1, 0)
    sf.set_channel_preset_index(2, 0)
    output = np.zeros((0, 2), dtype=np.float32)
    buffer = np.zeros((44100 * 1, 2), dtype=np.float32)

    sf.channel_note_on(0, 48, 1.0)
    sf.channel_note_on(1, 52, 1.0)
    sf.channel_note_on(2, 55, 1.0)
    sf.render(buffer)
    output = np.append(output, buffer)

    sf.set_channel_pan(0, 0)
    sf.set_channel_pitch_wheel(0, 16737)
    sf.set_channel_pan(1, 1)
    sf.set_channel_pan(2, 1)
    sf.render(buffer)
    output = np.append(output, buffer)

    sf.note_off()
    sf.render(buffer)
    output = np.append(output, buffer)
    scipy.io.wavfile.write('test.wav', 44100, output)

def test_all():
    test_help()
    test_load()
    test_chord()

test_all()
