import tinysoundfont

def test_help():
    import os
    os.environ['PAGER'] = 'cat'
    help(tinysoundfont)

def test_load():
    sf = tinysoundfont.SoundFont('test/example.sf2')
    assert sf.get_preset_count() == 1
    assert sf.get_preset_name(0) == 'El Cheapo Organ'

def test_wav():
    import numpy as np
    import scipy.io.wavfile
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.reset()
    sf.set_max_voices(8)
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.set_channel_preset_index(0, 0)
    sf.set_channel_preset_index(1, 0)
    sf.set_channel_preset_index(2, 0)
    output = np.zeros((0, 2), dtype=np.float32)
    buffer = np.zeros((44100 * 1, 2), dtype=np.float32)

    # 1 second silence
    output = np.concatenate((output, buffer))

    # 1 second chord
    sf.channel_note_on(0, 48, 1.0)
    sf.channel_note_on(1, 52, 1.0)
    sf.channel_note_on(2, 55, 1.0)
    sf.render(buffer)
    output = np.concatenate((output, buffer))

    # 1 second pitch bend
    sf.set_channel_pan(0, 0)
    sf.set_channel_pitch_wheel(0, 16737)
    sf.set_channel_pan(1, 1)
    sf.set_channel_pan(2, 1)
    sf.render(buffer)
    output = np.concatenate((output, buffer))

    # 1 second fadeout
    sf.note_off()
    sf.render(buffer)
    output = np.concatenate((output, buffer))

    # Write to WAV file
    scipy.io.wavfile.write('test.wav', 44100, output)

def test_blocking():
    import pyaudio
    import numpy as np
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(4),
                    channels=2,
                    rate=44100,
                    output=True)
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.reset()
    sf.set_max_voices(8)
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.set_channel_preset_index(0, 0)
    buffer = np.zeros((44100, 2), dtype=np.float32)

    # 1 second silence
    sf.render(buffer)
    stream.write(buffer.astype(np.float32).tobytes())

    # 1 second chord
    sf.channel_note_on(0, 48, 1.0)
    sf.channel_note_on(0, 52, 1.0)
    sf.channel_note_on(0, 55, 1.0)
    sf.render(buffer)
    stream.write(buffer.astype(np.float32).tobytes())

    # 1 second pan left with pitchbend down 2 semitones
    sf.set_channel_pan(0, 0)
    sf.set_channel_pitch_wheel(0, 0)
    sf.render(buffer)
    stream.write(buffer.astype(np.float32).tobytes())

    # 1 second fade-out
    sf.note_off()
    sf.render(buffer)
    stream.write(buffer.astype(np.float32).tobytes())

    stream.close()
    p.terminate()

def test_all():
    test_help()
    test_load()
    test_wav()
    test_blocking()

test_all()
