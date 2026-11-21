import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import chartlib as cl  # noqa: E402
import formclock as fc  # noqa: E402
import harmony as h  # noqa: E402

CH = lambda n: cl.load_chart(os.path.join(cl.ROOT, 'charts', n + '.yaml'))  # noqa: E731


def test_blues_clock_in_f_at_120():
    s = fc.Song(CH('blues_jazz'), key='F', bpm=120)          # 0.5 s per beat, 2 s per bar
    p = s.at(0.0)
    assert (p.chorus, p.bar, p.beat, p.chord.symbol) == (1, 1, 1, 'F7')
    p = s.at(2 * 5 + 0.1)                                     # bar 6
    assert (p.bar, p.chord.symbol) == (6, 'Bo7')
    p = s.at(2 * 3 + 1.0)                                     # bar 4 beat 3 -> I7 (after v-7)
    assert (p.bar, p.beat, p.chord.symbol) == (4, 3, 'F7')
    p = s.at(24 + 0.2)                                        # chorus 2, bar 1
    assert (p.chorus, p.bar, p.chord.symbol) == (2, 1, 'F7')
    assert s.at(2 * 11 + 1.2).next_chord.symbol == 'F7'       # last bar V7 -> back to the top


def test_count_in():
    s = fc.Song(CH('blues_jazz'), key='F', bpm=120)
    assert s.count_in_seconds() == 2.0
    p = s.at(-1.2)
    assert p.counting_in and p.beats_left == 3


def test_rhythm_changes_sections_and_key():
    s = fc.Song(CH('rhythm_changes'), key='Eb', bpm=200)      # 0.3 s per beat, 1.2 s per bar
    assert s.chorus_bars == 32
    p = s.at(1.2 * 16 + 0.01)                                 # bridge, bar 17
    assert (p.section, p.bar_in_section, p.chord.symbol) == ('B', 1, 'G7')
    p = s.at(1.2 * 15 + 0.01)                                 # end of A2 resolves to I6
    assert p.chord.symbol == 'Eb6'


def test_inheritance_basic_blues():
    c = CH('blues_basic')
    r = h.realize(c, 'Bb')
    assert [bar[0][0].symbol for bar in r['chorus']] == ['Bb7', 'Eb7', 'Bb7', 'Bb7', 'Eb7', 'Eb7', 'Bb7', 'Bb7',
                                                         'F7', 'Eb7', 'Bb7', 'F7']
    assert c['extends_from'] == 'blues_jazz' and c['tempo'] == {'bpm': 120}


def test_per_chord_scale_override():
    c = CH('blues_jazz')
    c['changes']['chorus'][7] = [['VI7', 4, {'scale': 'half_whole'}]]
    assert cl.check_chart(c) == []
    ch = h.realize(c, 'F')['chorus'][7][0][0]
    assert ch.symbol == 'D7' and ch.scale == 'half_whole'
    c['changes']['chorus'][7] = [['VI7', 4, {'scale': 'nonsense'}]]
    assert any('unknown scale' in p for p in cl.check_chart(c))


def test_tunings():
    assert h.parse_tuning('DADGCF') == ['D', 'A', 'D', 'G', 'C', 'F']
    assert h.parse_tuning('E A D G B E') == h.STANDARD
    std = {(s, f) for s, f, n, *_ in h.fretboard(h.chord('Dmaj7'), 'standard', 5) if n == 'D'}
    alt = {(s, f) for s, f, n, *_ in h.fretboard(h.chord('Dmaj7'), 'DADGCF', 5) if n == 'D'}
    assert (0, 0) in alt and (0, 0) not in std
    with pytest.raises(ValueError):
        h.parse_tuning('E A D H B E')


def test_sketch_without_changes_cannot_be_clocked():
    with pytest.raises(ValueError):
        fc.Song(CH('gangster_flick'))
