import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import chartlib as cl  # noqa: E402
import harmony as h  # noqa: E402


def test_letter_arithmetic_spelling():
    assert h.spell('C', 'b6') == 'Ab'          # not G#
    assert h.spell('C', 'bb7') == 'Bbb'        # dim7
    assert h.spell('Eb', '3') == 'G'
    assert h.spell('F#', '7') == 'E#'
    assert h.spell('Db', '#4') == 'G'


def test_numerals_in_keys():
    assert h.spell_numeral('bVI7', 'C') == 'Ab7'
    assert h.spell_numeral('#IVo7', 'F') == 'Bo7'
    assert h.spell_numeral('#IVo7', 'Bb') == 'Eo7'
    assert h.spell_numeral('ii-7', 'Db') == 'Eb-7'
    assert h.spell_numeral('VI7', 'Gb') == 'Eb7'
    assert h.spell_numeral('III7', 'Bb') == 'D7'


def test_dim7_keeps_its_double_flat():
    c = h.chord('#IVo7', 'C')                     # F#o7: F# A C Eb
    assert [n for n, _ in c.tones] == ['F#', 'A', 'C', 'Eb']
    c = h.chord('Co7')
    assert [n for n, _ in c.tones] == ['C', 'Eb', 'Gb', 'Bbb']


def test_scale_tones_and_weights():
    tones = h.chord('V7', 'F').scale_tones()      # C mixolydian
    names = [n for n, *_ in tones]
    assert names == ['C', 'D', 'E', 'F', 'G', 'A', 'Bb']
    w = {n: wt for n, _, _, wt in tones}
    assert w['C'] > w['E'] == w['Bb'] > w['G'] > w['D']


def test_fretboard_positions():
    pos = h.fretboard(h.chord('Cmaj7'), frets=12)
    roots = [(s, f) for s, f, n, *_ in pos if n == 'C']
    assert (1, 3) in roots and (4, 1) in roots and (0, 8) in roots
    assert all(0 <= f <= 12 for _, f, *_ in pos)


def test_charts_realize_in_any_key():
    for path, key, first in (('blues_jazz.yaml', 'F', 'F7'), ('blues_jazz.yaml', 'Db', 'Db7'),
                             ('rhythm_changes.yaml', 'Bb', 'Bbmaj7')):
        c = cl.load_chart(os.path.join(cl.ROOT, 'charts', path))
        r = h.realize(c, key)
        sec = c['form']['sections'][0]['name']
        assert r[sec][0][0][0].symbol == first
    r = h.realize(cl.load_chart(os.path.join(cl.ROOT, 'charts', 'blues_jazz.yaml')), 'Bb')
    assert r['chorus'][5][0][0].symbol == 'Eo7'


def test_every_spelled_note_has_a_colour():
    pal = cl.load_palette()
    assert cl.color_for('Bbb', pal) == pal['colors']['A']['start']
    assert cl.color_for('Fbb', pal) == pal['colors']['Eb']['start']
    for key in h.KEYS:
        for name, bars in h.realize(cl.load_chart(os.path.join(cl.ROOT, 'charts', 'rhythm_changes.yaml')), key).items():
            for bar in bars:
                for ch, _ in bar:
                    for n, *_ in ch.scale_tones():
                        cl.color_for(n, pal)


def test_numeral_needs_a_key():
    with pytest.raises(ValueError):
        h.chord('IV7')


def test_diminished_scale_keeps_chord_spelling():
    names = [n for n, *_ in h.chord('Bo7').scale_tones()]
    assert names == ['B', 'C#', 'D', 'E', 'F', 'G', 'Ab', 'A#']
    roles = {n: r for n, _, r, _ in h.chord('Bo7').scale_tones()}
    assert roles['Ab'] == 'guide' and roles['F'] == 'fifth'
