import tinysoundfont

def test_help():
    import os
    os.environ['PAGER'] = 'cat'
    help(tinysoundfont)

def test_load():
    i = tinysoundfont.SoundFont('test/example.sf2')
    print(i)
    i.reset()
    print(i.get_preset_count())
    print(i.get_preset_name(0))
    print(tinysoundfont.OutputMode.StereoInterleaved)
    i.set_output(tinysoundfont.OutputMode.StereoInterleaved, 44100, 0.0)
    o = tinysoundfont.SoundFont(i)
    print(o)

def test_all():
    test_help()
    test_load()

test_all()
