import tinysoundfont

def test_help():
    # Just make sure there is some text for `help(tinysoundfont)`
    import pydoc
    helptext = pydoc.render_doc(tinysoundfont, "%s")
    assert len(helptext.split('\n')) > 10

def test_load():
    sf = tinysoundfont.SoundFont('test/example.sf2')
    assert sf.get_preset_count() == 1
    assert sf.get_preset_name(0) == 'El Cheapo Organ'
    with open('test/example.sf2', 'rb') as f:
        mem = f.read()
        assert mem[:4] == b'RIFF'
        assert len(mem) == 3576
        sfmem = tinysoundfont.SoundFont(mem)
        assert sfmem.get_preset_count() == 1
        assert sfmem.get_preset_name(0) == 'El Cheapo Organ'

def test_bytes():
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.reset()
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.channel_set_preset_index(0, 0)
    sf.channel_note_on(0, 48, 1.0)
    bytes_per_float = 4
    channels = 2
    # Create 1 second buffer
    buffer = bytearray(44100 * bytes_per_float * channels)
    sf.render(buffer)
    # buffer now contains audio data
    # Check first and last value
    assert buffer[:4] == b'\x00\x00\x00\x00'
    assert buffer[-4:] == b'\x80\xc9\xd8='

def test_wav():
    import numpy as np
    import scipy.io.wavfile
    import tempfile
    import zlib
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.reset()
    sf.set_max_voices(8)
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.channel_set_preset_index(0, 0)
    sf.channel_set_preset_index(1, 0)
    sf.channel_set_preset_index(2, 0)
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
    sf.channel_set_pan(0, 0)
    sf.channel_set_pitch_wheel(0, 16737)
    sf.channel_set_pan(1, 1)
    sf.channel_set_pan(2, 1)
    sf.render(buffer)
    output = np.concatenate((output, buffer))

    # 1 second fadeout
    sf.note_off()
    sf.render(buffer)
    output = np.concatenate((output, buffer))

    # Write to WAV file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav') as wavfile:
        scipy.io.wavfile.write(wavfile.name, 44100, output)
        with open(wavfile.name, 'rb') as wavfileread:
            contents = wavfileread.read()
            # Check that WAV file has exactly right size
            assert len(contents) == 1411258
            # Check that WAV has right CRC32 (golden value)
            assert zlib.crc32(contents) == 0x6f378f91

def test_blocking():
    import pyaudio
    import numpy as np
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True)
    sf = tinysoundfont.SoundFont('/home/nwhitehead/ext/Downloads/MuseScore_General.sf3')
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, 8.0)
    sf.channel_set_preset_index(0, 1)
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
    sf.channel_set_pan(0, 0)
    sf.channel_set_pitch_wheel(0, 0)
    sf.render(buffer)
    stream.write(buffer.astype(np.float32).tobytes())

    # 1 second fade-out
    sf.note_off()
    sf.render(buffer)
    stream.write(buffer.astype(np.float32).tobytes())

    stream.close()
    p.terminate()

def test_blocking0():
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True)
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.channel_set_preset_index(0, 0)
    buffer = bytearray(44100 * 2 * 4)
    sf.channel_note_on(0, 48, 1.0)
    sf.render(buffer)
    stream.write(bytes(buffer))
    stream.close()
    p.terminate()

def test_callback0():
    import pyaudio
    import time
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        buffer = bytearray(frame_count * 2 * 4)
        sf.render(buffer)
        return (bytes(buffer), pyaudio.paContinue)

    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True,
                    stream_callback=callback)

    time.sleep(0.5)
    sf.channel_set_preset_index(0, 0)
    sf.channel_note_on(0, 48, 1.0)
    time.sleep(1)
    stream.close()
    p.terminate()

def test_callback():
    import pyaudio
    import numpy as np
    import time
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)

    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        buffer = np.zeros((frame_count, 2), dtype=np.float32)
        sf.render(buffer)
        return (buffer.astype(np.float32).tobytes(), pyaudio.paContinue)

    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True,
                    stream_callback=callback)

    time.sleep(1)

    sf.channel_set_preset_index(0, 0)
    sf.channel_note_on(0, 48, 1.0)
    sf.channel_note_on(0, 52, 1.0)
    sf.channel_note_on(0, 55, 1.0)
    time.sleep(1)

    sf.channel_set_pan(0, 1)
    sf.channel_set_pitch_wheel(0, 0)
    time.sleep(1)

    sf.note_off()
    time.sleep(1)

    stream.close()
    p.terminate()

def test_rerender():
    sf = tinysoundfont.SoundFont('test/example.sf2')
    sf.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, -18.0)
    sf.channel_set_preset_index(0, 0)
    bytes_per_float = 4
    channels = 2
    # Wrap with `memoryview` so slicing does not create copies but refers to subsections
    buffer = memoryview(bytearray(44100 * bytes_per_float * channels))
    start = 44100 * bytes_per_float * channels // 2
    sf.render(buffer[:start])
    sf.channel_note_on(0, 48, 1.0)
    sf.render(buffer[start:])
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True)
    stream.write(bytes(buffer))
    stream.close()
    p.terminate()

