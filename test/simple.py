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

def test_all():
    test_help()
    test_load()

test_all()
