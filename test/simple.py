import tinysoundfont

def test_help():
    import os
    os.environ['PAGER'] = 'cat'
    help(tinysoundfont)

def test_load():
    print(tinysoundfont.tsf_load_filename)
    i = tinysoundfont.SoundFont('test.sf2')
    print(i)

def test_all():
    test_help()
    test_load()

test_all()
