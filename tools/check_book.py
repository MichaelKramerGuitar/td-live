"""Check every chart in charts/ and the palette.   python tools/check_book.py"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as cl  # noqa: E402

ok = True
pal = cl.load_palette()
missing = [n for n in ('C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B')
           if n not in pal['colors']]
if missing:
    ok = False
    print('palette: missing', missing)
else:
    print('palette: %d spellings OK' % len(pal['colors']))

for path in sorted(glob.glob(os.path.join(cl.ROOT, 'charts', '*.yaml'))):
    try:
        chart = cl.resolve(cl._read(path), os.path.dirname(path))
        problems = cl.check_chart(chart)
    except (ValueError, OSError) as e:
        chart, problems = None, [str(e)]
    if problems:
        ok = False
        print('FAIL', os.path.basename(path))
        for p in problems:
            print('   -', p)
    else:
        print(cl.describe(chart))
sys.exit(0 if ok else 1)
