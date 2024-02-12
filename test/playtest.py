import pyaudio
import tinysoundfont
import numpy as np
import time

def test_callback():
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

test_callback()
