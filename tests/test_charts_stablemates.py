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
                 'F-7', 'Bb7alt', 'Eb-7', 'Ab7alt', 'Dbmaj7', 'C7alt']   # A1 turns into the bridge
    bridge = [e[2].symbol for e in s.events if 15 <= e[6] <= 22]
    assert bridge == ['F-7', 'Gb13', 'G7alt', 'C7', 'B7', 'Bb7', 'A7', 'Ab7']


def test_stablemates_melody_and_phrasing():
    import harmony as h
    c = cl.load_chart(os.path.join(cl.ROOT, 'charts', 'stablemates.yaml'))
    s = fc.Song(c, key='Db')
    f = [(s.events[i][2].symbol, n, h.chord_function(s.events[i][2].root, n, s.events[i][2].quality))
         for i in range(2) for n in s.melody_for(i)]
    assert f == [('E-7', 'F#', '9'), ('A7', 'F#', '13')]          # the 9 becomes the 13
    assert s.melody[4] == ['Ab'] and s.melody[8] == ['C', 'E']   # null carries; one node per chord
    a = c['form']['sections'][0]
    assert cl.phrasing_text(a, 0) == '2+8 · 4' and cl.phrasing_text(a, 1) == '8+2 · 4'
    assert cl.check_chart(c) == []
    last_a1 = [i for i, e in enumerate(s.events) if e[6] == 14][0]
    assert s.melody_for(last_a1) == ['Eb'] and h.chord_function('C', 'Eb', '7alt') == '#9'
    assert [e[2].symbol for e in s.events if e[6] == 36] == ['Dbmaj7']
