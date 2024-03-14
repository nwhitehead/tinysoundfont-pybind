
import numpy as np
import pydoc
import scipy.io.wavfile
import tempfile
import time
import zlib

import tinysoundfont

PAN_CONTROL = 10

def test_help():
    # Just make sure there is some text for `help(tinysoundfont)`
    helptext = pydoc.render_doc(tinysoundfont, "%s")
    assert len(helptext.split("\n")) > 10


def test_load():
    s = tinysoundfont.Synth()
    sfid = s.sfload("test/florestan-piano.sf2")
    assert s.sfpreset_name(sfid, 0, 0) == "Piano"
    with open("test/florestan-piano.sf2", "rb") as f:
        mem = f.read()
        assert mem[:4] == b"RIFF"
        assert len(mem) == 187548
        sfid2 = s.sfload(mem)
        assert s.sfpreset_name(sfid2, 0, 0) == "Piano"


def test_bytes():
    s = tinysoundfont.Synth(gain=-14)
    sfid = s.sfload("test/florestan-piano.sf2")
    s.program_select(0, sfid, 0, 0)
    s.noteon(0, 48, 100)
    # Create 1 second buffer
    buffer = s.generate(44100)
    # buffer now contains audio data
    # Check first and last value
    assert buffer[:4] == b"\x99\xfa\xac\xba"
    assert buffer[-4:] == b"\xc6z\x97;"


def test_wav():
    s = tinysoundfont.Synth(gain=-14)
    sfid = s.sfload("test/florestan-piano.sf2")
    s.program_select(0, sfid, 0, 0)
    s.program_select(1, sfid, 0, 0)
    s.program_select(2, sfid, 0, 0)

    buffer = bytearray()
    buffer.extend(s.generate(44100))

    s.noteon(0, 48, 100)
    s.noteon(1, 52, 100)
    s.noteon(2, 55, 100)

    buffer.extend(s.generate(44100))

    # 1 second pitch bend

    s.control_change(0, PAN_CONTROL, 0)
    s.control_change(1, PAN_CONTROL, 64)
    s.control_change(2, PAN_CONTROL, 127)
    s.pitchbend(0, 16737)
    s.pitchbend(1, 16737)
    s.pitchbend(2, 16737)

    buffer.extend(s.generate(44100))

    # 1 second fadeout

    s.noteoff(0, 48)
    s.noteoff(1, 52)
    s.noteoff(2, 55)

    buffer.extend(s.generate(44100))

    # Convert bytearray value into numpy (samples, 2) matrix in float32 format
    output = np.reshape(np.frombuffer(buffer, dtype=np.float32), (-1, 2))

    # Write to WAV file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".wav") as wavfile:
        scipy.io.wavfile.write(wavfile.name, 44100, output)
        with open(wavfile.name, "rb") as wavfileread:
            contents = wavfileread.read()
            # Check that WAV file has exactly right size
            assert len(contents) == 1411258
            # Check that WAV has right CRC32 (golden value)
            assert zlib.crc32(contents) == 3997000505


def test_start():
    s = tinysoundfont.Synth(gain=-14)
    sfid = s.sfload("test/florestan-piano.sf2")
    s.program_select(0, sfid, 0, 0)
    s.program_select(1, sfid, 0, 0)
    s.program_select(2, sfid, 0, 0)
    s.pitchbend_range(0, 12.0)
    s.pitchbend_range(1, 12.0)
    s.pitchbend_range(2, 12.0)
    s.start(buffer_size=2048)

    time.sleep(1.0)

    s.noteon(0, 48, 100)
    s.noteon(1, 52, 100)
    s.noteon(2, 55, 100)

    time.sleep(1.0)

    s.pitchbend(0, 0)
    s.pitchbend(1, 8192)
    s.pitchbend(2, 0)
    s.control_change(0, PAN_CONTROL, 0)
    s.control_change(1, PAN_CONTROL, 64)
    s.control_change(2, PAN_CONTROL, 127)

    time.sleep(1.0)

    s.noteoff(0, 48)
    s.noteoff(1, 52)
    s.noteoff(2, 55)

    time.sleep(1.0)

    s.stop()
