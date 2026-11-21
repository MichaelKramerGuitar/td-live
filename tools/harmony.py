"""Harmony engine: Roman-numeral charts -> spelled chords -> chord-scales -> weights -> fretboard.

Pure Python (no TouchDesigner), shared by the tools, the tests and later TD.

Everything is SPELLED with letter arithmetic, never semitone counting: bVI in C is Ab (not G#), the
diminished seventh of C is Bbb. Michael's synesthesia colours follow spelling, so this matters.

    import harmony as h
    h.spell_numeral('bVI7', 'C')          # 'Ab7'
    h.chord('#IVo7', 'Bb')                # Chord(root='E', quality='o7', ...)
    h.chord('V7', 'F').scale_tones()      # [('C', '1'), ('D', '2'), ('E', '3'), ...]
    h.fretboard(h.chord('ii-7', 'F'))     # [(string, fret, 'G', '1', weight), ...]

Roman numerals are always relative to the MAJOR scale of the key (jazz convention): in C minor the
relative major chord is 'bIIImaj7', the tonic 'i-7' (case is decorative; the quality suffix decides).
"""
import re
from dataclasses import dataclass, field

LETTERS = 'CDEFGAB'
NATURAL_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]                     # semitones of scale degrees 1..7
ACC_TEXT = {-2: 'bb', -1: 'b', 0: '', 1: '#', 2: '##'}

# Key signatures Michael can pick (conventional spellings decide the colours).
KEYS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']


# ---------------------------------------------------------------- spelling
def parse_note(s):
    m = re.match(r'^([A-G])(bb|b|##|#)?$', s)
    if not m:
        raise ValueError('not a spelled note: %r' % s)
    acc = {None: 0, 'b': -1, 'bb': -2, '#': 1, '##': 2}[m.group(2)]
    return m.group(1), acc


def pc(note):
    letter, acc = parse_note(note)
    return (NATURAL_PC[letter] + acc) % 12


def spell(root, interval):
    """root 'Eb', interval '3' / 'b7' / 'bb7' / '#11' / '9' -> spelled note (letter arithmetic)."""
    m = re.match(r'^(bb|b|##|#)?(\d+)$', interval)
    if not m:
        raise ValueError('bad interval %r' % interval)
    alt = {None: 0, 'b': -1, 'bb': -2, '#': 1, '##': 2}[m.group(1)]
    n = int(m.group(2)) - 1
    letter, _ = parse_note(root)
    new_letter = LETTERS[(LETTERS.index(letter) + n) % 7]
    target = (pc(root) + MAJOR_STEPS[n % 7] + alt) % 12
    acc = (target - NATURAL_PC[new_letter] + 6) % 12 - 6
    if acc not in ACC_TEXT:
        raise ValueError('cannot spell %s above %s' % (interval, root))
    return new_letter + ACC_TEXT[acc]


# ---------------------------------------------------------------- chord qualities
# quality -> (chord tones, default chord-scale). Intervals relative to the chord root.
# Chord-scale defaults are a starting point; a chart can override per chord with "scale:".
QUALITIES = {
    'maj7': (['1', '3', '5', '7'], 'ionian'),
    '6':    (['1', '3', '5', '6'], 'ionian'),
    '':     (['1', '3', '5'], 'ionian'),
    '7':    (['1', '3', '5', 'b7'], 'mixolydian'),
    '-7':   (['1', 'b3', '5', 'b7'], 'dorian'),
    '-6':   (['1', 'b3', '5', '6'], 'melodic_minor'),
    '-':    (['1', 'b3', '5'], 'dorian'),
    'ø7':   (['1', 'b3', 'b5', 'b7'], 'locrian'),
    'o7':   (['1', 'b3', 'b5', 'bb7'], 'diminished'),
    '7alt': (['1', '3', 'b7'], 'altered'),
}
ALIASES = {'m7': '-7', 'min7': '-7', 'm6': '-6', 'm': '-', 'dim7': 'o7', 'm7b5': 'ø7', 'h7': 'ø7',
           'M7': 'maj7', 'Δ7': 'maj7', 'Δ': 'maj7', 'alt': '7alt'}

SCALES = {   # intervals from the chord root, in order
    'ionian':        ['1', '2', '3', '4', '5', '6', '7'],
    'lydian':        ['1', '2', '3', '#4', '5', '6', '7'],
    'mixolydian':    ['1', '2', '3', '4', '5', '6', 'b7'],
    'dorian':        ['1', '2', 'b3', '4', '5', '6', 'b7'],
    'aeolian':       ['1', '2', 'b3', '4', '5', 'b6', 'b7'],
    'phrygian':      ['1', 'b2', 'b3', '4', '5', 'b6', 'b7'],
    'locrian':       ['1', 'b2', 'b3', '4', 'b5', 'b6', 'b7'],
    'melodic_minor': ['1', '2', 'b3', '4', '5', '6', '7'],
    'lydian_dominant': ['1', '2', '3', '#4', '5', '6', 'b7'],
    'altered':       ['1', 'b2', '#2', '3', '#4', 'b6', 'b7'],
    'diminished':    ['1', '2', 'b3', '4', 'b5', 'b6', '6', '7'],          # whole-half
    'half_whole':    ['1', 'b2', '#2', '3', '#4', '5', '6', 'b7'],
}

# How much "mass" each kind of tone has (Michael: mass ~ importance for grounding the harmony).
WEIGHTS = {'root': 1.0, 'guide': 0.6, 'fifth': 0.35, 'chord': 0.45, 'tension': 0.15}


def tone_role(interval, chord_tones):
    num = int(re.sub(r'\D', '', interval))
    if num == 1:
        return 'root'
    if interval in chord_tones:
        return 'guide' if num in (3, 7) else ('fifth' if num == 5 else 'chord')
    return 'tension'


@dataclass
class Chord:
    root: str
    quality: str
    symbol: str
    numeral: str = ''
    scale: str = ''
    tones: list = field(default_factory=list)       # [(note, interval)]

    def scale_tones(self):
        """[(spelled note, interval, role, weight)] for the whole chord-scale. Chord tones keep the chord's
        own spelling (Bo7's Ab, not G#); scale tones that sound like a chord tone are replaced by it."""
        chord_iv = [iv for _, iv in self.tones]
        out = []
        for iv in SCALES[self.scale]:
            note = spell(self.root, iv)
            match = [civ for civ in chord_iv if pc(spell(self.root, civ)) == pc(note)]
            if match:
                iv = match[0]
                note = spell(self.root, iv)
            if any(pc(note) == pc(n) for n, _, _, _ in out):
                continue
            role = tone_role(iv, chord_iv)
            out.append((note, iv, role, WEIGHTS[role]))
        for civ in chord_iv:                        # chord tones the scale doesn't contain (rare)
            note = spell(self.root, civ)
            if not any(pc(note) == pc(n) for n, _, _, _ in out):
                role = tone_role(civ, chord_iv)
                out.append((note, civ, role, WEIGHTS[role]))
        return out


_NUMERAL = re.compile(r'^(b|#)?(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)(.*)$')
_ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
_SYMBOL = re.compile(r'^([A-G](?:bb|b|##|#)?)(.*)$')


def _quality(q):
    q = ALIASES.get(q, q)
    if q not in QUALITIES:
        raise ValueError('unknown chord quality %r' % q)
    return q


def numeral_root(numeral, key):
    m = _NUMERAL.match(numeral)
    if not m:
        raise ValueError('not a Roman numeral chord: %r' % numeral)
    acc, rn, q = m.groups()
    deg = _ROMAN[rn.upper()]
    return spell(key, (acc or '') + str(deg)), q


def chord(symbol_or_numeral, key=None, scale=None):
    """A Chord from 'Ab7' (absolute) or from 'bVI7' + key."""
    s = symbol_or_numeral
    if _NUMERAL.match(s) and not _SYMBOL.match(s):
        if key is None:
            raise ValueError('%r is a Roman numeral: a key is needed' % s)
        root, q = numeral_root(s, key)
        numeral = s
    else:
        m = _SYMBOL.match(s)
        if not m:
            raise ValueError('not a chord: %r' % s)
        root, q = m.groups()
        numeral = ''
    q = _quality(q)
    tones_iv, default_scale = QUALITIES[q]
    c = Chord(root=root, quality=q, symbol=root + q, numeral=numeral, scale=scale or default_scale)
    c.tones = [(spell(root, iv), iv) for iv in tones_iv]
    return c


def spell_numeral(numeral, key):
    return chord(numeral, key).symbol


def is_numeral(s):
    return bool(_NUMERAL.match(s)) and not _SYMBOL.match(s)


# ---------------------------------------------------------------- fretboard
# Open strings, LOW to HIGH. Standard is the default; alternate tunings are a Config choice in TDlive.
TUNINGS = {
    'standard': ['E', 'A', 'D', 'G', 'B', 'E'],
    'DADGCF':   ['D', 'A', 'D', 'G', 'C', 'F'],          # "8 Little Prayers"
    'drop_D':   ['D', 'A', 'D', 'G', 'B', 'E'],
    'DADGAD':   ['D', 'A', 'D', 'G', 'A', 'D'],
}
STANDARD = TUNINGS['standard']


def parse_tuning(t):
    """'standard' / 'DADGCF' / 'E A D G B E' / ['E', ...] -> list of spelled open strings, low to high."""
    if isinstance(t, (list, tuple)):
        notes = list(t)
    elif t in TUNINGS:
        notes = TUNINGS[t]
    else:
        notes = t.replace(',', ' ').split()
    for n in notes:
        parse_note(n)
    return notes


def fretboard(c, tuning=STANDARD, frets=19):
    """Every position of the chord-scale: [(string 0=low, fret, note, interval, role, weight)]."""
    tones = c.scale_tones()
    by_pc = {pc(n): (n, iv, role, w) for n, iv, role, w in tones}
    out = []
    for s, open_note in enumerate(parse_tuning(tuning)):
        base = pc(open_note)
        for f in range(frets + 1):
            hit = by_pc.get((base + f) % 12)
            if hit:
                out.append((s, f) + hit)
    return out


# ---------------------------------------------------------------- charts in numerals
def realize(chart, key):
    """Spell a chart's `changes` in a key. Returns {section: [[(Chord, beats), ...] per bar]}.
    A chord entry is [symbol, beats] or [symbol, beats, {scale: <name>}] (per-chord chord-scale override)."""
    absolute = chart.get('changes_notation', 'absolute') != 'roman'
    out = {}
    for name, bars in (chart.get('changes') or {}).items():
        sec = []
        for bar in bars:
            row = []
            for entry in bar:
                sym, beats = entry[0], entry[1]
                opts = entry[2] if len(entry) > 2 else {}
                row.append((chord(sym, None if absolute else key, scale=opts.get('scale')), beats))
            sec.append(row)
        out[name] = sec
    return out
