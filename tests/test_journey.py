import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import journey as j  # noqa: E402


def test_cohorts_match_michaels_lists():
    assert j.minor_third_cohort('C') == ['C', 'Eb', 'Gb', 'A']
    assert [j.major_third_cohort(k) for k in ('C', 'Db', 'D', 'Eb')] == [
        ['C', 'E', 'Ab'], ['Db', 'F', 'A'], ['D', 'F#', 'Bb'], ['Eb', 'G', 'B']]


def test_torus_every_key_once():
    cells = {j.torus(k) for k in j.KEY_NAMES.values()}
    assert len(cells) == 12
    for k in j.minor_third_cohort('C'):
        assert j.torus(k)[0] == j.torus('C')[0]
    for k in j.major_third_cohort('C'):
        assert j.torus(k)[1] == j.torus('C')[1]


def test_perfect_cadence_family_spelled_toward_c():
    fam = {f['role']: f for f in j.perfect_cadence_family('C')}
    assert [fam[r]['dominant'] for r in ('V7', 'bVII7', 'bII7', 'III7')] == ['G7', 'Bb7', 'Db7', 'E7']
    assert fam['V7']['dim7'] == ['B', 'D', 'F', 'Ab']
    assert fam['bVII7']['dim7'] == ['D', 'F', 'Ab', 'Cb']
    assert fam['bII7']['dim7'] == ['F', 'Ab', 'Cb', 'Ebb']
    assert fam['III7']['dim7'] == ['G#', 'B', 'D', 'F']


def test_plagal_family():
    assert [f['chord'] for f in j.plagal_family('C')] == ['F-6', 'Ab-6', 'B-6', 'D-6']


def test_stablemates_bar_1():
    # Michael: A7 = tritone sub of the secondary dominant of Ab7 (Eb7); E-7 = A7 ii'd
    assert j.secondary_dominant('Ab') == ('Eb7', 'A7')
    assert j.related_ii('A7') == 'E-7'
    assert {f['role']: f['dominant'] for f in j.perfect_cadence_family('Ab')}['bII7'] == 'A7'


def test_tension_dials():
    t, parts = j.tension('Db', 'Db', 'Dbmaj7')
    assert t == 0
    t2, parts2 = j.tension('Db', 'Db', 'A7', depth=2)
    assert parts2['outside'] == 3 and t2 > t        # A, E, G are outside Db major (C# = Db is in)


def test_attya_and_betty_spell_as_michael_wrote():
    import chartlib as cl
    import formclock as fc
    for cid, want in (('all_the_things_you_are', 'D-7 G7'), ('along_came_betty', 'B-9 E13')):
        s = fc.Song(cl.load_chart(os.path.join(cl.ROOT, 'charts', cid + '.yaml')), key='Ab')
        assert cl.check_chart(s.chart) == []
        bars = {}
        for e in s.events:
            bars.setdefault(e[6], []).append(e[2].symbol)
        assert ' '.join(bars[6 if cid.startswith('all') else 2]) == want


def test_performance_meter_refits_chords():
    import chartlib as cl
    import formclock as fc
    c = cl.load_chart(os.path.join(cl.ROOT, 'charts', 'all_the_things_you_are.yaml'))
    for meter, split, acc in (('7:4+3', [4, 3], [1, 5]), ('7:3+4', [3, 4], [1, 4]), ('3', [2, 1], [1])):
        s = fc.Song(c, key='Ab', meter=meter)
        assert [e[1] for e in s.events if e[6] == 6] == split and s.accents == acc
        assert s.chorus_beats == 36 * s.beats_per_bar


def test_endings_last_chorus():
    import chartlib as cl
    import formclock as fc
    s = fc.Song(cl.load_chart(os.path.join(cl.ROOT, 'charts', 'all_the_things_you_are.yaml')), key='Ab', bpm=60)
    bar36 = 35 * 4 + 0.5                                       # seconds at 60 bpm = beats
    assert s.at(bar36).chord.symbol == 'C7alt'                 # looping: the turnaround
    assert s.at(bar36, last=1).chord.symbol == 'Abmaj7'        # last chorus: the ending
    assert s.ending_bar == 36
    assert not s.at(36 * 4 + 1, last=1).finished               # ringing the final chord
    assert s.at(36 * 4 + 1, last=1).chord.symbol == 'Abmaj7'
    assert s.at(37 * 4 + 0.1, last=1).finished


def test_journey_plan_reads_michaels_roles():
    import chartlib as cl
    import formclock as fc
    s = fc.Song(cl.load_chart(os.path.join(cl.ROOT, 'charts', 'all_the_things_you_are.yaml')), key='Ab')
    plan = j.journey_plan(s)
    by_bar = {}
    for ev, p in zip(s.events, plan):
        by_bar.setdefault(ev[6], []).append(p['local'])
    assert by_bar[1] == ['Ab'] and by_bar[6] == ['C', 'C'] and by_bar[7] == ['C']
    assert by_bar[14] == ['G', 'G'] and by_bar[23] == ['E'] and by_bar[25] == ['Ab']
    b = fc.Song(cl.load_chart(os.path.join(cl.ROOT, 'charts', 'along_came_betty.yaml')), key='Ab')
    bp = {}
    for ev, p in zip(b.events, j.journey_plan(b)):
        bp.setdefault(ev[6], []).append(p['local'])
    assert bp[5] == ['A'] and bp[9] == ['E']        # Amaj13 arrives; A2 is about E (ii/#V)
