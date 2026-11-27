"""The harmony model behind the Journey modes (plan step 1: no visuals).

Michael's Harmony Journey (claude.ai project: harmony-journey/HARMONY_JOURNEY.md, DECISIONS.md), built on:
  - Dan Tepfer, "Tonal Harmony in 3D" (blog post 2023-10-14, dantepfer.com/blog, and its video): tonal centres
    as stars, diatonic chords as planets, secondary chords as orbits; home as a valley.
  - Barry Harris: a dim7 chord is a rootless dominant 7b9.
  - The key torus (pitch class mod 3 x mod 4) follows from Michael's minor-third and major-third cohorts.
Everything is spelled (letter arithmetic, tools/harmony.py): spelling says which cohort member is the target.

    import journey as j
    j.minor_third_cohort('C')         # ['C', 'Eb', 'Gb', 'A']
    j.major_third_cohort('D')         # ['D', 'F#', 'Bb']
    j.torus('C')                      # (0, 0)
    j.perfect_cadence_family('C')     # the four dominants (G7 Bb7 Db7 E7) + their rootless dim7s
    j.plagal_family('C')              # F-6 Ab-6 B-6 D-6
    j.related_ii('A7')                # 'E-7'   (any V can be ii'd)
    j.tension(...)                    # weighted dials
"""
import harmony as h

# ---------------------------------------------------------------- keys
KEY_NAMES = {0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F', 6: 'Gb', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}


def key_accidentals(key):
    """Signed number of sharps (+) / flats (-) in a major key's signature, from its spelling."""
    scale = [h.spell(key, str(d)) for d in range(1, 8)]
    n = 0
    for note in scale:
        _, acc = h.parse_note(note)
        n += acc
    return n


def practical_key(key):
    """A playable spelling of a major key: no double accidentals, at most 7 in the signature
    (G# major -> Ab, A# -> Bb, Bbb -> A). Keys that are already practical keep their spelling (F# stays F#)."""
    _, acc = h.parse_note(key)
    if abs(acc) < 2 and abs(key_accidentals(key)) <= 7:
        return key
    return KEY_NAMES[h.pc(key)]


def walk(key, interval, steps):
    """Keys reached by stacking an interval, each spelled from the one before it."""
    out = [key]
    for _ in range(steps - 1):
        out.append(practical_key(h.spell(out[-1], interval)))
    return out


# ---------------------------------------------------------------- cohorts and the torus
def minor_third_cohort(key):
    """The secondary-chord cohort: C Eb Gb A (3 such cohorts)."""
    return walk(key, 'b3', 4)


def major_third_cohort(key):
    """The mediant cohort: C E Ab (4 such cohorts)."""
    return walk(key, '3', 3)


def torus(key):
    """(minor-third cohort index 0..2, major-third cohort index 0..3). Every key is the one meeting point of its
    two cohorts, so the 12 keys tile a 3 x 4 grid that wraps both ways."""
    p = h.pc(key)
    return p % 3, p % 4


def torus_distance(a, b):
    (a3, a4), (b3, b4) = torus(a), torus(b)
    d3 = min((a3 - b3) % 3, (b3 - a3) % 3)
    d4 = min((a4 - b4) % 4, (b4 - a4) % 4)
    return d3 + d4


def fifths_distance(a, b):
    """Steps around the circle of fifths (0..6)."""
    d = ((h.pc(b) - h.pc(a)) * 7) % 12
    return min(d, 12 - d)


# ---------------------------------------------------------------- secondary chord families
def rootless(dominant):
    """A dominant's rootless 7b9 = its dim7 (3, 5, b7, b9), spelled from the dominant (Barry Harris)."""
    return [h.spell(dominant, iv) for iv in ('3', '5', 'b7', 'b9')]


def perfect_cadence_family(target):
    """The four dominants that point at `target`, a minor third apart, with their rootless dim7s spelled toward
    the target: V7 (G7 -> C), bVII7 (Bb7, backdoor), bII7 (Db7, tritone sub), III7 (E7, the exotic one)."""
    out = []
    for name, iv in (('V7', '5'), ('bVII7', 'b7'), ('bII7', 'b2'), ('III7', '3')):
        root = practical_key(h.spell(target, iv))     # bII of Ab is A, not Bbb
        out.append({'role': name, 'dominant': root + '7', 'dim7': rootless(root), 'target': target})
    return out


def plagal_family(target):
    """The minor-6 plagal cadences to `target`: iv-6, bvi-6, vii-6, ii-6 (each holds one of the vii-dim7's
    tritones). Spelled from their roots (B-6 = B D F# G#); the Cb-6 spelling toward C is an open question."""
    out = []
    for name, iv in (('iv-6', '4'), ('bvi-6', 'b6'), ('vii-6', '7'), ('ii-6', '2')):
        c = h.chord(h.spell(target, iv) + '-6')
        out.append({'role': name, 'chord': c.symbol, 'tones': [n for n, _ in c.tones], 'target': target})
    return out


def related_ii(dominant_symbol):
    """Any V can be ii'd: the minor 7 a fifth above the dominant's root (A7 -> E-7)."""
    root = h.chord(dominant_symbol).root
    return h.spell(root, '5') + '-7'


def secondary_dominant(target_root):
    """V7 of a chord root, and its tritone sub: ('Eb7', 'A7') for Ab."""
    return practical_key(h.spell(target_root, '5')) + '7', practical_key(h.spell(target_root, 'b2')) + '7'


# ---------------------------------------------------------------- tension dials
DEFAULT_WEIGHTS = {'fifths': 1.0, 'torus': 0.5, 'depth': 1.0, 'outside': 0.5}


def outside_tones(chord_symbol, home):
    """Chord tones not in the home major scale (by pitch)."""
    home_pcs = {h.pc(h.spell(home, str(d))) for d in range(1, 8)}
    return [n for n, _ in h.chord(chord_symbol).tones if h.pc(n) not in home_pcs]


def tension(home, local_key, chord_symbol, depth=0, weights=None):
    """How hard the tether pulls: weighted dials (Michael: all of these matter, make them configurable).
    home / local_key: major keys; depth: how many secondary layers deep (0 = diatonic to the local key)."""
    w = dict(DEFAULT_WEIGHTS, **(weights or {}))
    parts = {'fifths': fifths_distance(home, local_key),
             'torus': torus_distance(home, local_key),
             'depth': depth,
             'outside': len(outside_tones(chord_symbol, home))}
    return sum(w[k] * v for k, v in parts.items()), parts


# ---------------------------------------------------------------- reading Michael's analysis
import re as _re

_TARGET = _re.compile(r'/\s*(b|#)?(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)\b')
_PLAIN = _re.compile(r'^(b|#)?(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)(maj|alt|[-+\u00f8\u00b0o0-9#b])*$')


def role_of(chart, section, bar_in_section, chord_in_bar):
    """Michael's role string for a chord (chart `analysis`), or ''."""
    bars = (chart.get('analysis') or {}).get(section) or []
    if bar_in_section - 1 >= len(bars) or not bars[bar_in_section - 1]:
        return ''
    roles = bars[bar_in_section - 1]
    return str(roles[min(chord_in_bar, len(roles) - 1)] or '')


def journey_plan(song):
    """For every chord event of a formclock.Song: where it lives in the journey.
    [{'role', 'local' (root of the local tonic, spelled), 'minor' (local tonic is minor), 'depth'}].
    Rules (from Michael's hearing): 'x/Y' -> local tonic Y (of the home key); a plain numeral (vi, ii, V7 ...)
    -> home; 'arrival' -> the chord's own root becomes the local tonic; anything else carries the last one on."""
    out, local, minor = [], song.key, False
    per_bar = {}
    for ev in song.events:
        n = per_bar.get(ev[6], 0)
        per_bar[ev[6]] = n + 1
        role = role_of(song.chart, ev[3], ev[5], n)
        depth = role.count('/')
        m = _TARGET.search(role)
        if m:
            acc, rn = m.group(1) or '', m.group(2)
            local = practical_key(h.spell(song.key, acc + str(h._ROMAN[rn.upper()])))
            minor = rn.islower()
        elif 'arrival' in role.lower():
            local, minor = practical_key(ev[2].root), ev[2].quality.startswith(('-', 'ø', 'o'))
        elif _PLAIN.match(role.split(' ')[0] if role else ''):
            local, minor = song.key, False
        out.append({'role': role, 'local': local, 'minor': minor, 'depth': depth})
    return out


# ---------------------------------------------------------------- gestural function (Michael, 2026-11-27)
# When the key elements are evoked, not every rule has to be followed for the ear to hear tension and release:
# root movement and voice leading carry the function even when the chord quality doesn't (Tadd Dameron's Lady
# Bird turnaround: I VI7 II7 V7 -> C Eb7 Ab7 Db7 -> Cmaj7 Ebmaj7 Abmaj7 Dbmaj7; Sam Rivers' Beatrice:
# Gbmaj7#11 -> Fmaj7, Ebmaj7 -> D-7, and the falling line D-7 C-7 Bb-7 A-7).
def gestural(chord, next_chord, prev_chord=None):
    """How a chord gestures toward the next one by root movement alone (whatever its quality):
    'subV'  - root a half step above the next root (the tritone-sub dominant's motion)
    'V'     - root a fifth above the next root (the dominant's motion)
    'line'  - part of a stepwise run of same-quality chords (a directional line)
    ''      - none of these. Returns (kind, is_softened): softened = the quality isn't a dominant 7."""
    d = (h.pc(chord.root) - h.pc(next_chord.root)) % 12
    dominant = chord.quality.startswith('7') or chord.quality in ('9', '13', '7b9', '7alt')
    if d == 1:
        return 'subV', not dominant
    if d == 7:
        return 'V', not dominant
    if prev_chord is not None:
        same = chord.quality == next_chord.quality == prev_chord.quality
        steps = {(h.pc(prev_chord.root) - h.pc(chord.root)) % 12, (h.pc(chord.root) - h.pc(next_chord.root)) % 12}
        if same and steps <= {1, 2} or same and steps <= {10, 11}:
            return 'line', False
    return '', False
