import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import chartlib as cl  # noqa: E402

GF = os.path.join(cl.ROOT, 'charts', 'gangster_flick.yaml')


def test_gangster_flick_form():
    c = cl.load_chart(GF)
    assert [(n, b) for n, _, b in cl.form_plan(c)] == [('A', 8)] * 4 + [('B', 12)] + [('C', 20)] * 2
    assert cl.total_bars(c) == 84


def test_enharmonics_sound_the_same_but_look_different():
    pal = cl.load_palette()
    assert cl.pitch_class('C#') == cl.pitch_class('Db') == 1
    assert cl.color_for('C#', pal) != cl.color_for('Db', pal)


def test_circle_of_fifths_positions():
    assert [cl.fifths_index(p) for p in ('C', 'G', 'D', 'F#', 'Gb', 'Db', 'F')] == [0, 1, 2, 6, 6, 7, 11]


def test_chord_roots_keep_their_spelling():
    assert cl.chord_root('Abm9') == 'Ab'
    assert cl.chord_root('C#7alt') == 'C#'
    with pytest.raises(ValueError):
        cl.chord_root('m7')


def test_undecided_spelling_and_fallback():
    pal = cl.load_palette()
    assert cl.color_for('F#/Gb', pal) == pal['colors']['F#']['start']
    assert cl.color_for('Cb', pal) == pal['colors']['B']['start']


def test_changes_are_checked_against_form_and_meter():
    c = cl.load_chart(GF)
    c['changes'] = {'B': [[['Abm7', 5]]] * 11 + [[['Db7', 3], ['Gb', 1]]]}
    probs = cl.check_chart(c)
    assert probs == ['changes/B bar 12: chords add up to 4 beats, meter has 5']
    c['changes'] = {'B': [[['Abm7', 5]]] * 10}
    assert any('10 bars written, form says 12' in p for p in cl.check_chart(c))


def test_schema_rejects_bad_spelling():
    c = cl.load_chart(GF)
    c['pitch']['melodic_nodes'] = ['H']
    assert cl.check_chart(c)
