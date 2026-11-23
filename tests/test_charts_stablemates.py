import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import chartlib as cl  # noqa: E402
import formclock as fc  # noqa: E402


def test_stablemates_in_db_matches_michaels_chart():
    s = fc.Song(cl.load_chart(os.path.join(cl.ROOT, 'charts', 'stablemates.yaml')), key='Db')
    assert s.chorus_bars == 36
    a = []
    for e in s.events:
        if e[6] <= 14:
            a.append(e[2].symbol)
    assert a == ['E-7', 'A7', 'Eb-7', 'Ab7', 'Dbmaj7', 'C7alt', 'Ab-7', 'Db7', 'Gbmaj7', 'Gø7', 'C7alt',
                 'F-7', 'Bb7alt', 'Eb-7', 'Ab7alt', 'Dbmaj7', 'Dbmaj7']
    bridge = [e[2].symbol for e in s.events if 15 <= e[6] <= 22]
    assert bridge == ['F-7', 'Gb13', 'G7alt', 'C7', 'B7', 'Bb7', 'A7', 'Ab7']
