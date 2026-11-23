# Three-circle notation -> drawing primitives (Script TOP callbacks for visuals/notation/prims).
# Michael's notation (docs/NOTATION.md), drawn live from the chart + the song clock + the pitch follower:
#   OUTER  rhythm: a polygon with one side per beat (square = 4/4); balls on it = the chart's accents; a light
#          travels the perimeter with the beat.
#   MIDDLE pitch: the circle of fifths (C at the top). Its 12 nodes take the palette colour of their spelling,
#          larger for the current chord-scale (or become note names: Names). Harmony circles sit on it at each
#          chord's root: OUTSIDE = major, INSIDE = minor; each is itself a little circle of fifths - fixed do
#          (C at its top) or movable do (the chord's root at its top) - whose polygon joins the chord tones.
#          The current chord is lit, the next half lit, the rest of the tune faint (the harmonic map).
#          Melodic nodes from the chart: a ring on the circle of fifths + a ring at that note inside the
#          current harmony circle (so you see what it is over the chord: 9, 13, b13 ...).
#          Notes you play flare on the ring and are joined in order (your line as a constellation).
#   INNER  form as phrasing: the current phrase group's shape (sides = bars), spokes at its sub-groups, the bar
#          being played filling in gold; little shapes below = this section's phrase groups; dots above =
#          the sections in play order.
# Output: one column per primitive (see draw.frag): rows (type, ax, ay, bx) (by, half width, glow, alpha) (rgb).
# Alpha < 0 subtracts light (used to clear the ring behind note names).
import math
import time

import numpy as np

MAXP = 768
R_RING = 0.46            # circle of fifths
R_OFF = 0.13             # harmony circle centre distance from the ring (outside major / inside minor)
R_HC = 0.082             # harmony circle radius
R_OUT = 0.80             # outer polygon in-radius
R_FORM = 0.15            # phrase shape circumradius
FLATS = ['C', 'G', 'D', 'A', 'E', 'B', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']
SHARPS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
WHITE, GOLD = (1.0, 0.97, 0.92), (1.0, 0.85, 0.55)
_MEM = {'notes': [], 'names': []}         # played notes [pc, spelled, t_start, t_last]; ring labels for names


def onSetupParameters(scriptOp):
    return


def E():
    return op.Song.op('engine').module


def fifths_angle(pc):
    return ((pc * 7) % 12) * (2 * math.pi / 12)          # 0 = top, clockwise


def on_circle(angle, r, cx=0.0, cy=0.0):
    return cx + r * math.sin(angle), cy + r * math.cos(angle)


def poly_vertices(n, r_in=None, r_circ=None, cx=0.0, cy=0.0):
    """Flat-top regular polygon, vertices clockwise from the left end of the top side (n + 1 points)."""
    rc = r_circ if r_circ is not None else r_in / math.cos(math.pi / n)
    out = []
    for k in range(n + 1):
        th = math.pi / 2 + math.pi / n - 2 * math.pi * k / n
        out.append((cx + rc * math.cos(th), cy + rc * math.sin(th)))
    return out


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def is_minor(q):
    return q.startswith('-') or q.startswith('ø') or q.startswith('o')


class Prims:
    def __init__(self):
        self.a = np.zeros((3, MAXP, 4), np.float32)
        self.a[0, :, 0] = -1
        self.n = 0

    def add(self, t, ax, ay, bx, by, w, glow, alpha, rgb):
        if self.n >= MAXP - 1 or abs(alpha) <= 0.003:
            return
        i = self.n
        self.a[0, i] = (t, ax, ay, bx)
        self.a[1, i] = (by, w, glow, alpha)
        self.a[2, i] = (rgb[0], rgb[1], rgb[2], 0)
        self.n += 1

    def line(self, a, b, w, alpha, rgb, glow=0.0):
        self.add(0, a[0], a[1], b[0], b[1], w, glow, alpha, rgb)

    def ring(self, c, r, w, alpha, rgb, glow=0.0):
        self.add(1, c[0], c[1], r, 0, w, glow, alpha, rgb)

    def disc(self, c, r, alpha, rgb, glow=0.0):
        self.add(2, c[0], c[1], r, 0, 0, glow, alpha, rgb)


def colour(note):
    import chartlib as cl
    try:
        return cl.hex_to_rgb(cl.color_for(note, E().palette()))
    except Exception:
        return (0.7, 0.7, 0.7)


def phrasing_choice(s):
    """Which hearing of the phrasing: visuals/notation › Phrasing (1st / 2nd / alternate every chorus)."""
    m = op.Visuals.op('notation').par.Phrasing.eval()
    if m == 'alternate':
        return max(0, int(op.Song.op('out')['chorus'].eval()) - 1)
    return 1 if m == 'second' else 0


def state():
    """Everything both the drawing and the caption need about 'now'."""
    s = E().song()
    if s is None:
        return None
    clk = op.Song.op('out')
    playing = clk['playing'].eval() > 0.5
    st = {'s': s, 'active': clk['active'].eval() > 0.5, 'playing': playing,
          'beat': int(clk['beat'].eval()) if playing else 1,
          'phase': clk['beat_phase'].eval() if playing else 0.0,
          'bar': int(clk['bar'].eval()) if playing else 1,
          'bar_phase': clk['bar_phase'].eval() if playing else 0.0}
    b = (st['bar'] - 1) * s.beats_per_bar + (st['beat'] - 1) + st['phase']
    idx = 0
    for i, ev in enumerate(s.events):
        if ev[0] <= b + 1e-6:
            idx = i
        else:
            break
    st['idx'] = idx
    st['cur'] = s.events[idx][2]
    st['nxt'] = s.events[(idx + 1) % len(s.events)][2]
    st['mel'] = s.melody_for(idx)
    st['mel_next'] = s.melody_for((idx + 1) % len(s.events))
    return st


def onCook(scriptOp):
    absTime.frame                                   # cook every frame (trails fade with time)
    P = Prims()
    L = parent()
    st = state()
    if st is None:
        _MEM['names'] = []
        scriptOp.copyNumpyArray(P.a)
        return
    import harmony as h
    import chartlib as cl
    s, playing, beat, phase, bar = st['s'], st['playing'], st['beat'], st['phase'], st['bar']
    cur, nxt = st['cur'], st['nxt']
    movable = L.par.Do.eval() == 'movable'
    names_on = L.par.Names.eval()
    tones_t = op.Song.op('tones')
    tone_w = {r[0].val: float(r[3].val) for r in tones_t.rows()[1:]} if tones_t.numRows > 1 else {}

    # ---- OUTER: rhythm polygon, accents, the travelling beat
    meter = s.chart['rhythm']['meter']['beats']
    V = poly_vertices(meter, r_in=R_OUT)
    for k in range(meter):
        lit = playing and k == beat - 1
        P.line(V[k], V[k + 1], 0.0035, 0.55 if lit else 0.22, WHITE, 0.6 if lit else 0.15)
        P.disc(V[k], 0.006, 0.5, WHITE)
    for acc in s.chart['rhythm'].get('accents') or []:
        k = int(math.floor(acc - 1)) % meter
        pt = lerp(V[k], V[k + 1], (acc - 1) - math.floor(acc - 1))
        hot = playing and abs(((beat - 1) + phase) - (acc - 1)) < 0.18
        P.disc(pt, 0.022 if hot else 0.016, 0.9 if hot else 0.5, (1.0, 0.82, 0.55), 1.2 if hot else 0.3)
    if st['active']:
        k = (beat - 1) % meter
        P.disc(lerp(V[k], V[k + 1], phase), 0.012, 1.0, WHITE, 1.5)

    # ---- MIDDLE: circle of fifths with the chord-scale (or note names)
    flat_key = ('b' in s.key) or s.key == 'F'
    names = FLATS if flat_key else SHARPS
    P.ring((0, 0), R_RING, 0.0025, 0.25, WHITE, 0.1)
    spelled_now = {h.pc(t): t for t in tone_w}
    for t in st['mel']:                               # the melody's spelling wins on its own pitch
        spelled_now[h.pc(t)] = t
    labels = []
    for i in range(12):
        pc = (i * 7) % 12
        name = spelled_now.get(pc, names[i])
        w = tone_w.get(name, 0.0)
        pt = on_circle(fifths_angle(pc), R_RING)
        if names_on:
            P.disc(pt, 0.026, -1.0, WHITE)            # clear the ring behind the letter
            labels.append((pt, name, 0.45 + 0.55 * min(1.0, w * 1.5) if name in tone_w else 0.4))
            if w > 0:
                P.ring(pt, 0.027, 0.0015, 0.25 + 0.5 * w, colour(name), 0.5 * w)
        else:
            P.disc(pt, 0.010 + 0.016 * w, 0.35 + 0.65 * min(1.0, w * 1.5) if name in tone_w else 0.25,
                   colour(name), 0.8 * w)
    _MEM['names'] = labels

    def tone_angle(note, root):
        a = fifths_angle(h.pc(note))
        return a - fifths_angle(h.pc(root)) if movable else a

    def harmony_circle(ch, alpha, glow, width):
        rr = R_RING - R_OFF if is_minor(ch.quality) else R_RING + R_OFF
        c = on_circle(fifths_angle(h.pc(ch.root)), rr)
        P.ring(c, R_HC, width, alpha, colour(ch.root), glow)
        pts = sorted(((tone_angle(note, ch.root) % (2 * math.pi), note) for note, iv in ch.tones))
        vs = [(on_circle(a, R_HC * 0.82, c[0], c[1]), note) for a, note in pts]
        for j in range(len(vs)):
            if len(vs) > 2 or j == 0:
                P.line(vs[j][0], vs[(j + 1) % len(vs)][0], width * 0.8, alpha * 0.9, colour(ch.root), glow * 0.5)
        for v, note in vs:
            P.disc(v, 0.008 if note != ch.root else 0.012, alpha, colour(note), glow)
        return c

    if L.par.Allchords.eval():
        seen = set()
        for ev in s.events:
            ch = ev[2]
            key = (ch.root, ch.quality)
            if key in seen or key in ((cur.root, cur.quality), (nxt.root, nxt.quality)):
                continue
            seen.add(key)
            harmony_circle(ch, 0.16, 0.0, 0.0018)
    if (nxt.root, nxt.quality) != (cur.root, cur.quality):
        harmony_circle(nxt, 0.42, 0.2, 0.0022)
    c = harmony_circle(cur, 1.0, 0.9, 0.003)
    P.line(on_circle(fifths_angle(h.pc(cur.root)), R_RING), c, 0.0015, 0.4, colour(cur.root), 0.3)

    # ---- melodic nodes (from the chart): on the ring, and where they sit inside the current chord
    for t in st['mel_next']:
        if t not in st['mel']:
            P.ring(on_circle(fifths_angle(h.pc(t)), R_RING), 0.024, 0.0018, 0.35, colour(t), 0.1)
    for t in st['mel']:
        pt = on_circle(fifths_angle(h.pc(t)), R_RING)
        P.ring(pt, 0.03, 0.003, 1.0, colour(t), 0.9)
        P.ring(pt, 0.03, 0.0012, 0.9, WHITE, 0.0)
        inner = on_circle(tone_angle(t, cur.root), R_HC * 0.82, c[0], c[1])
        P.ring(inner, 0.016, 0.0022, 1.0, colour(t), 0.8)

    # ---- live melodic nodes from the pitch follower
    now = time.time()
    trail = L.par.Melodytrail.eval()
    a = op.Analysis.op('out')
    try:
        clarity, level, midi = a['clarity'].eval(), a['level'].eval(), a['midi'].eval()
    except Exception:
        clarity, level, midi = 0, 0, 0
    if clarity >= L.par.Melodyclarity.eval() and level > 0.04 and midi > 0:
        pc = int(round(midi)) % 12
        notes = _MEM['notes']
        if notes and notes[-1][0] == pc:
            notes[-1][3] = now
        else:
            notes.append([pc, spelled_now.get(pc, names[(pc * 7) % 12]), now, now])
    _MEM['notes'] = [n_ for n_ in _MEM['notes'] if now - n_[3] < trail][-24:]
    prev = None
    for pc, name, t0, t1 in _MEM['notes']:
        f = max(0.0, 1.0 - (now - t1) / trail)
        pt = on_circle(fifths_angle(pc), R_RING)
        P.disc(pt, 0.014 + 0.012 * f, f, colour(name), 1.6 * f)
        if prev is not None:
            P.line(prev[0], pt, 0.0022, 0.7 * min(f, prev[1]), colour(name), 0.5 * f)
        prev = (pt, f)

    # ---- INNER: form as phrasing
    si, start, nbars, sname = s.span_at(bar)
    sec = {x['name']: x for x in s.chart['form']['sections']}.get(sname, {'shape': nbars})
    groups = cl.phrasing_groups(sec, phrasing_choice(s))
    bis = bar - start + 1                              # bar within the section
    gi, gstart = 0, 1
    for gi, g in enumerate(groups):
        if bis < gstart + sum(g):
            break
        gstart += sum(g)
    g = groups[gi]
    n = max(2, sum(g))
    pos = bis - gstart                                 # 0-based bar within the phrase group
    FV = poly_vertices(n, r_circ=R_FORM)
    for k in range(n):
        done = playing and k < pos
        P.line(FV[k], FV[k + 1], 0.003, 0.6 if done else 0.22, WHITE, 0.2 if done else 0.0)
    if len(g) > 1:                                     # spokes where the sub-groups begin
        acc_ = 0
        for sub in g:
            P.line((0, 0), FV[acc_ % n], 0.0022, 0.45, GOLD, 0.2)
            P.disc(FV[acc_ % n], 0.009, 0.8, GOLD, 0.4)
            acc_ += sub
    if playing:
        m = lerp(FV[pos], FV[pos + 1], st['bar_phase'])
        P.line(FV[pos], m, 0.005, 1.0, GOLD, 1.0)
        P.disc(m, 0.009, 1.0, GOLD, 1.2)
    if len(g) > 1 and not sec.get('phrasings'):        # no phrasing written: zig-zag = passes around
        zw = R_FORM * 0.9
        pts = [(-zw / 2 + zw * j / len(g), (0.03 if j % 2 == 0 else -0.03)) for j in range(len(g) + 1)]
        for j in range(len(g)):
            on = playing and j == pos // g[0]
            P.line(pts[j], pts[j + 1], 0.0028, 0.9 if on else 0.3, GOLD if on else WHITE, 0.6 if on else 0.0)
    for j in range(int(sec.get('hashes', 0))):
        x = -0.02 * (int(sec.get('hashes', 0)) - 1) / 2 + 0.02 * j
        P.line((x - 0.006, -R_FORM * 0.55), (x + 0.006, -R_FORM * 0.35), 0.002, 0.5, WHITE)
    if len(groups) > 1:                                # this section's phrase groups, small, below
        for j, gg in enumerate(groups):
            x = (j - (len(groups) - 1) / 2) * 0.06
            here = j == gi
            mv = poly_vertices(max(2, sum(gg)), r_circ=0.02, cx=x, cy=-0.205)
            for k in range(len(mv) - 1):
                P.line(mv[k], mv[k + 1], 0.0018, 0.9 if here else 0.3, GOLD if here else WHITE, 0.3 if here else 0)
    for j in range(len(s.spans)):                      # sections in play order, above
        x = (j - (len(s.spans) - 1) / 2) * 0.034
        here = playing and j == si
        P.disc((x, 0.205), 0.011 if here else 0.006, 1.0 if here else 0.35, GOLD if here else WHITE,
               0.8 if here else 0)

    scriptOp.copyNumpyArray(P.a)
    return


def names_table(dat):
    """Fill the Text TOP spec table with the ring's note names (Names on): x, y in pixels from the centre."""
    dat.clear()
    dat.appendRow(['text', 'x', 'y', 'alpha'])
    W, H = op.Config.par.Width.eval(), op.Config.par.Height.eval()
    unit = min(W, H) / 2.0
    for pt, name, alpha in _MEM['names']:
        dat.appendRow([name.replace('b', '♭').replace('#', '♯'), W / 2 + pt[0] * unit,
                       H / 2 + pt[1] * unit, round(alpha, 2)])


def label():
    """Caption: section, bar, chord -> next, and what the melodic node is over the chord."""
    st = state()
    if st is None:
        return ''
    import harmony as h
    s, bar = st['s'], st['bar']
    si, start, nbars, name = s.span_at(bar)
    cur, nxt = st['cur'], st['nxt']
    txt = '%s   %s   bar %d/%d      %s  →  %s' % (s.chart['title'], name, bar - start + 1, nbars,
                                                      cur.symbol, nxt.symbol)
    mel = st['mel']
    if mel:
        parts = []
        for t in mel:
            f = h.chord_function(cur.root, t, cur.quality)
            if t in st['mel_next'] and (nxt.root, nxt.quality) != (cur.root, cur.quality):
                f += ' → ' + h.chord_function(nxt.root, t, nxt.quality)
            parts.append('%s  %s' % (t, f))
        txt += '      melody ' + ',  '.join(parts)
    return txt


def phrasing_label():
    """For the TDlive window's PHRASING button: '2+8 · 4', '8+2 · 4', 'Alternate' or 'as written'."""
    import chartlib as cl
    s = E().song()
    if s is None:
        return '—'
    m = op.Visuals.op('notation').par.Phrasing.eval()
    if m == 'alternate':
        return 'Alternate'
    choice = 1 if m == 'second' else 0
    for sec in s.chart['form']['sections']:
        if sec.get('phrasings'):
            return cl.phrasing_text(sec, choice)
    return 'as written'
