# Melodic gesture whisp (Script CHOP /project1/visuals/landscape/gesture, callbacks synced to this file).
# Not a transcription: it follows the CONTOUR of single-note lines over the fretboard. Each frame with a confident
# pitch (analysis/pitch) releases a small glowing puff at a plausible place for that note on the neck (staying near
# the current hand position), coloured by Michael's palette (spelled to fit the current chord). Puffs drift up and
# sideways and fade, so an 8th-note line leaves a zephyr-like trail that traces its shape.
# Out: one sample per puff - tx ty tz (world), s (size), r g b (colour), a (opacity).
import math
import os
import random
import sys

TOOLS = os.path.join(project.folder, 'tools')
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import chartlib as cl   # noqa: E402
import harmony as h     # noqa: E402

STD_OPEN = [40, 45, 50, 55, 59, 64]          # standard tuning, MIDI, low to high
YMAX, NECK_L, STRING_W = 0.70, 40.0, 1.0      # same world as the landscape (build_landscape.py)
MAXPUFFS = 260
_PAL = {}
_STATE = {}       # per-op memory (module level: storing on the op itself makes it re-cook in a loop)


def onSetupParameters(scriptOp):
    return


def fret_y(n):
    return 1.0 - 2.0 ** (-n / 12.0)


def open_midi(tuning):
    """MIDI note of each open string for any tuning (octave taken from standard tuning, nearest pitch class)."""
    out = []
    for s, name in enumerate(h.parse_tuning(tuning)):
        base = STD_OPEN[min(s, 5)]
        d = (h.pc(name) - base) % 12
        out.append(base + (d - 12 if d > 6 else d))
    return out


def spell(midi_round):
    """Spell the played pitch class to fit the current chord-scale; otherwise by key signature."""
    pcls = midi_round % 12
    tones = op.Song.op('tones')
    for r in range(1, tones.numRows):
        n = tones[r, 'note'].val
        try:
            if h.pc(n) == pcls:
                return n
        except ValueError:
            pass
    flats = {0: 'C', 1: 'Db', 2: 'D', 3: 'Eb', 4: 'E', 5: 'F', 6: 'Gb', 7: 'G', 8: 'Ab', 9: 'A', 10: 'Bb', 11: 'B'}
    sharps = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
    use_flats = True
    s = op.Song.op('engine').module.song()
    if s is not None and ('#' in s.key or s.key in ('G', 'D', 'A', 'E', 'B')):
        use_flats = False
    return (flats if use_flats else sharps)[pcls]


def colour(note):
    if 'pal' not in _PAL:
        _PAL['pal'] = cl.load_palette(os.path.join(project.folder, 'synesthesia', 'palette.yaml'))
    return cl.hex_to_rgb(cl.color_for(note, _PAL['pal']))


def place(midi, st, frets, tuning):
    """Choose (string, fret) for a note: near the current hand position, small string jumps."""
    opens = open_midi(tuning)
    hand, last_s = st['hand'], st['last_s']
    best = None
    for s, o in enumerate(opens):
        f = int(round(midi)) - o
        if 0 <= f <= frets:
            cost = abs(f - hand) + 0.8 * abs(s - last_s) + (0.6 if f == 0 else 0.0)
            if best is None or cost < best[0]:
                best = (cost, s, f)
    return None if best is None else best[1:]


def onCook(scriptOp):
    L = parent()
    dt = 1.0 / max(1.0, project.cookRate)
    st = _STATE.get(scriptOp.path)
    if st is None:
        st = {'puffs': [], 'hand': 5.0, 'last_s': 2.5, 'note': None, 'head': None}
    pitch = op.Analysis.op('pitch')
    bus = op.Analysis.op('out')
    on = L.par.Gesture.eval()
    midi = pitch['midi'].eval() if pitch is not None else 0.0
    clarity = pitch['clarity'].eval() if pitch is not None else 0.0
    level = bus['level'].eval() if bus is not None else 0.0
    hit = bus['hit'].eval() if bus is not None else 0.0
    frets = op.Song.par.Frets.eval()
    tuning = op.Config.par.Tuning.eval()
    flip = L.par.Flip.eval()

    if on and midi > 0 and clarity >= L.par.Gestureclarity.eval():
        pos = place(midi, st, frets, tuning)
        if pos is not None:
            s, f = pos
            note_i = int(round(midi))
            new_note = note_i != st['note']
            if new_note:
                st['hand'] += 0.35 * (f - st['hand'])
                st['last_s'] = s
                st['note'] = note_i
                st['rgb'] = colour(spell(note_i))
            y = -0.02 if f == 0 else 0.5 * (fret_y(f - 1) + fret_y(f))
            sx = (5.0 - s) if flip else float(s)
            target = ((sx - 2.5) * STRING_W, -(YMAX - y) * NECK_L)
            head = st['head'] or target
            k = 0.55                                         # glide between notes (legato-ish contour)
            head = (head[0] + k * (target[0] - head[0]), head[1] + k * (target[1] - head[1]))
            st['head'] = head
            energy = min(1.0, level * 1.5)
            size = L.par.Gesturesize.eval() * (0.6 + 0.7 * energy + (0.8 if new_note else 0.0) + 0.6 * hit)
            r, g, b = st.get('rgb', (1, 1, 1))
            st['puffs'].append([head[0], 0.25 + 0.3 * hit, head[1], size, r, g, b, 0.0,
                                random.uniform(0, 6.28), 1.0 if new_note else 0.55])
    else:
        st['head'] = None if clarity < 0.3 else st['head']

    life = max(0.2, L.par.Gesturetrail.eval())
    rise, drift = L.par.Gesturerise.eval(), L.par.Gesturedrift.eval()
    keep = []
    for p in st['puffs']:
        p[7] += dt                                           # age
        if p[7] < life:
            p[1] += rise * dt
            p[0] += math.sin(p[7] * 1.7 + p[8]) * drift * dt
            p[2] += math.cos(p[7] * 1.3 + p[8]) * drift * 0.6 * dt
            keep.append(p)
    st['puffs'] = keep[-MAXPUFFS:]
    _STATE[scriptOp.path] = st

    n = max(1, len(st['puffs']))
    scriptOp.clear()
    scriptOp.numSamples = n
    chans = {c: scriptOp.appendChan(c) for c in ('tx', 'ty', 'tz', 's', 'r', 'g', 'b', 'a')}
    for i, p in enumerate(st['puffs']):
        fade = (1.0 - p[7] / life) ** 1.5 * p[9]
        grow = 1.0 + 1.6 * (p[7] / life)                    # puffs swell as they dissipate
        vals = (p[0], p[1], p[2], p[3] * grow, p[4] * fade, p[5] * fade, p[6] * fade, fade)
        for c, v in zip(('tx', 'ty', 'tz', 's', 'r', 'g', 'b', 'a'), vals):
            chans[c][i] = v
    if not st['puffs']:
        for c in chans.values():
            c[0] = 0.0
    return
