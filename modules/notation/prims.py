# Three-circle notation -> drawing primitives (Script TOP callbacks for visuals/notation/prims).
# Michael's notation (docs/NOTATION.md), drawn live from the chart + the song clock + the pitch follower:
#   OUTER  rhythm: a polygon with one side per beat (square = 4/4); balls on it = the chart's accents; a light
#          travels the perimeter with the beat.
#   MIDDLE pitch: the circle of fifths (C at the top). Its 12 nodes take the palette colour of their spelling,
#          larger for the current chord-scale. Harmony circles sit on it at each chord's root: OUTSIDE = major,
#          INSIDE = minor; each is itself a little circle of fifths (C at its top) whose polygon joins the chord
#          tones, so its shape shows the chord's interval structure. The current chord is lit, the next one
#          half lit, the rest of the tune faint (the tune's harmonic map). Notes you play flare on the ring and
#          are joined in order (your line as a constellation in fifths-space).
#   INNER  form: the current section's shape (sides = bars), the zig-zag multiplier and repeat hashes, the bar
#          being played filling as it goes; dots below = the sections in play order.
# Output: one column per primitive (see draw.frag): rows (type, ax, ay, bx) (by, half width, glow, alpha) (rgb).
import math
import time

import numpy as np

MAXP = 768
R_RING = 0.46            # circle of fifths
R_OFF = 0.13             # harmony circle centre distance from the ring (outside major / inside minor)
R_HC = 0.082             # harmony circle radius
R_OUT = 0.80             # outer polygon in-radius
R_FORM = 0.15            # form shape circumradius
FLATS = ['C', 'G', 'D', 'A', 'E', 'B', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']
SHARPS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
_MEM = {'notes': [], 'last_pc': None}      # played notes: [pc, spelled, t_start, t_last]  (module memory)


def onSetupParameters(scriptOp):
    return


def E():
    return op.Song.op('engine').module


def fifths_angle(pc):
    return ((pc * 7) % 12) * (2 * math.pi / 12)          # 0 = top, clockwise


def on_circle(angle, r, cx=0.0, cy=0.0):
    return cx + r * math.sin(angle), cy + r * math.cos(angle)


def poly_vertices(n, r_in=None, r_circ=None):
    """Flat-top regular polygon, vertices clockwise from the left end of the top side."""
    rc = r_circ if r_circ is not None else r_in / math.cos(math.pi / n)
    out = []
    for k in range(n + 1):
        th = math.pi / 2 + math.pi / n - 2 * math.pi * k / n
        out.append((rc * math.cos(th), rc * math.sin(th)))
    return out


def is_minor(q):
    return q.startswith('-') or q.startswith('ø') or q.startswith('o')


class Prims:
    def __init__(self):
        self.a = np.zeros((3, MAXP, 4), np.float32)
        self.a[0, :, 0] = -1
        self.n = 0

    def add(self, t, ax, ay, bx, by, w, glow, alpha, rgb):
        if self.n >= MAXP - 1 or alpha <= 0.003:
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
    pal = E().palette()
    import chartlib as cl
    try:
        return cl.hex_to_rgb(cl.color_for(note, pal))
    except Exception:
        return (0.7, 0.7, 0.7)


def onCook(scriptOp):
    absTime.frame                                   # cook every frame (trails fade with time)
    P = Prims()
    L = parent()
    s = E().song()
    if s is None:
        scriptOp.copyNumpyArray(P.a)
        return
    clk = op.Song.op('out')
    active = clk['active'].eval() > 0.5
    playing = clk['playing'].eval() > 0.5
    beat = int(clk['beat'].eval()) if playing else 1
    phase = clk['beat_phase'].eval() if playing else 0.0
    bar = int(clk['bar'].eval()) if playing else 1
    bpb = s.beats_per_bar
    every = L.par.Allchords.eval()
    white = (1.0, 0.97, 0.92)

    # ---- where are we: current / next chord event
    b = (bar - 1) * bpb + (beat - 1) + phase
    idx = 0
    for i, ev in enumerate(s.events):
        if ev[0] <= b + 1e-6:
            idx = i
        else:
            break
    cur = s.events[idx][2]
    nxt = s.events[(idx + 1) % len(s.events)][2]
    tones = [r[0].val for r in op.Song.op('tones').rows()[1:]] if op.Song.op('tones').numRows > 1 else []
    tone_w = {r[0].val: float(r[3].val) for r in op.Song.op('tones').rows()[1:]} if tones else {}

    # ---- OUTER: rhythm polygon, accents, the travelling beat
    meter = s.chart['rhythm']['meter']['beats']
    V = poly_vertices(meter, r_in=R_OUT)
    for k in range(meter):
        lit = playing and k == beat - 1
        P.line(V[k], V[k + 1], 0.0035, 0.55 if lit else 0.22, white, 0.6 if lit else 0.15)
        P.disc(V[k], 0.006, 0.5, white)
    for acc in s.chart['rhythm'].get('accents') or []:
        k = int(math.floor(acc - 1)) % meter
        t = (acc - 1) - math.floor(acc - 1)
        pt = (V[k][0] + (V[k + 1][0] - V[k][0]) * t, V[k][1] + (V[k + 1][1] - V[k][1]) * t)
        hot = playing and abs(((beat - 1) + phase) - (acc - 1)) < 0.18
        P.disc(pt, 0.022 if hot else 0.016, 0.9 if hot else 0.5, (1.0, 0.82, 0.55), 1.2 if hot else 0.3)
    if active:
        k = (beat - 1) % meter
        pt = (V[k][0] + (V[k + 1][0] - V[k][0]) * phase, V[k][1] + (V[k + 1][1] - V[k][1]) * phase)
        P.disc(pt, 0.012, 1.0, white, 1.5)

    # ---- MIDDLE: circle of fifths, chord-scale nodes, harmony circles
    flat_key = ('b' in s.key) or s.key == 'F'
    names = FLATS if flat_key else SHARPS
    P.ring((0, 0), R_RING, 0.0025, 0.25, white, 0.1)
    import harmony as h
    spelled_now = {h.pc(t): t for t in tones}
    for i in range(12):
        pc = (i * 7) % 12
        name = spelled_now.get(pc, names[i])
        w = tone_w.get(name, 0.0)
        pt = on_circle(fifths_angle(pc), R_RING)
        P.disc(pt, 0.010 + 0.016 * w, 0.35 + 0.65 * min(1.0, w * 1.5) if name in tone_w else 0.25,
               colour(name), 0.8 * w)

    def harmony_circle(ch, alpha, glow, width):
        ang = fifths_angle(h.pc(ch.root))
        rr = R_RING - R_OFF if is_minor(ch.quality) else R_RING + R_OFF
        c = on_circle(ang, rr)
        P.ring(c, R_HC, width, alpha, colour(ch.root), glow)
        pts = []
        for note, iv in ch.tones:
            pts.append((fifths_angle(h.pc(note)), note))
        pts.sort()
        vs = [(on_circle(a, R_HC * 0.82, c[0], c[1]), note) for a, note in pts]
        for j in range(len(vs)):
            a_, b_ = vs[j][0], vs[(j + 1) % len(vs)][0]
            if len(vs) > 2 or j == 0:
                P.line(a_, b_, width * 0.8, alpha * 0.9, colour(ch.root), glow * 0.5)
        for v, note in vs:
            P.disc(v, 0.008 if note != ch.root else 0.012, alpha, colour(note), glow)
        return c

    if every:
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
    # a thread from the ring node of the root to its harmony circle
    P.line(on_circle(fifths_angle(h.pc(cur.root)), R_RING), c, 0.0015, 0.4, colour(cur.root), 0.3)

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
            name = spelled_now.get(pc, names[(pc * 7) % 12])
            notes.append([pc, name, now, now])
    _MEM['notes'] = [n_ for n_ in _MEM['notes'] if now - n_[3] < trail][-24:]
    prev = None
    for pc, name, t0, t1 in _MEM['notes']:
        f = max(0.0, 1.0 - (now - t1) / trail)
        pt = on_circle(fifths_angle(pc), R_RING)
        P.disc(pt, 0.014 + 0.012 * f, f, colour(name), 1.6 * f)
        if prev is not None:
            P.line(prev[0], pt, 0.0022, 0.7 * min(f, prev[1]), colour(name), 0.5 * f)
        prev = (pt, f)

    # ---- INNER: form
    i, start, nbars, name = s.span_at(bar)
    sec = {x['name']: x for x in s.chart['form']['sections']}.get(name, {'shape': nbars})
    shape = max(2, int(sec.get('shape', nbars)))
    mult = max(1, int(sec.get('multiplier', 1)))
    hashes = int(sec.get('hashes', 0))
    bis = bar - start + 1
    lap = (bis - 1) // shape
    side = (bis - 1) % shape
    bar_phase = clk['bar_phase'].eval() if playing else 0.0
    FV = poly_vertices(shape, r_circ=R_FORM)
    gold = (1.0, 0.85, 0.55)
    for k in range(shape):
        done = playing and k < side
        P.line(FV[k], FV[k + 1], 0.003, 0.6 if done else 0.22, white, 0.2 if done else 0.0)
    if playing:
        a_, b_ = FV[side], FV[side + 1]
        m = (a_[0] + (b_[0] - a_[0]) * bar_phase, a_[1] + (b_[1] - a_[1]) * bar_phase)
        P.line(a_, m, 0.005, 1.0, gold, 1.0)
        P.disc(m, 0.009, 1.0, gold, 1.2)
    if mult > 1:                                        # zig-zag: one stroke per pass around the shape
        zw = R_FORM * 0.9
        pts = [(-zw / 2 + zw * j / mult, (0.03 if j % 2 == 0 else -0.03)) for j in range(mult + 1)]
        for j in range(mult):
            on = playing and j == lap
            P.line(pts[j], pts[j + 1], 0.0028, 0.9 if on else 0.3, gold if on else white, 0.6 if on else 0.0)
    for j in range(hashes):
        x = -0.02 * (hashes - 1) / 2 + 0.02 * j
        P.line((x - 0.006, -R_FORM * 0.55), (x + 0.006, -R_FORM * 0.35), 0.002, 0.5, white)
    # play order
    n = len(s.spans)
    for j, (st, nb, nm) in enumerate(s.spans):
        x = (j - (n - 1) / 2) * 0.034
        here = playing and j == i
        P.disc((x, -0.215), 0.011 if here else 0.006, 1.0 if here else 0.35, gold if here else white, 0.8 if here else 0)

    scriptOp.copyNumpyArray(P.a)
    return


def label():
    """Small caption: section, bar, chord -> next (visuals/notation › Labels)."""
    s = E().song()
    if s is None:
        return ''
    clk = op.Song.op('out')
    playing = clk['playing'].eval() > 0.5
    bar = int(clk['bar'].eval()) if playing else 1
    i, start, nbars, name = s.span_at(bar)
    now = op.Song.op('now')
    try:
        ch, nx = now['chord', 1].val, now['next', 1].val
    except Exception:
        ch = nx = ''
    return '%s   %s   bar %d/%d      %s  →  %s' % (s.chart['title'], name, bar - start + 1, nbars, ch, nx)
