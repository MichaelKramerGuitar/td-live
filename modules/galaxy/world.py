# Harmony Galaxy, first picture (Script TOP callbacks for visuals/galaxy/prims).
# Michael's Harmony Journey (claude.ai project: harmony-journey/), after Dan Tepfer's "Tonal Harmony in 3D":
#   - The 12 keys are stars. Home sits at the bottom of the deepest valley; every other key is placed by its
#     distance around the circle of fifths (V and IV close, the tritone key far out on the rim), so going
#     further from home means climbing. Home's cohorts (minor-third: C Eb Gb A; major-third/Coltrane: C E Ab)
#     dig their own, shallower valleys: lesser but similar gravity.
#   - The local tonic (from Michael's analysis in the chart) is the star the music orbits now: its 7 diatonic
#     chords are planets around it (in fifths order: IV I V ii vi iii vii), the current chord lit.
#   - Secondary chords (roles 'x/Y') are moons circling the planet/star they point at.
#   - A comet (the traveller) glides from chord to chord leaving a trail; a tether runs from it back home,
#     tighter and redder as the tension dials rise (tools/journey.py).
# Drawn as 2D primitives (modules/notation/draw.frag) after a 3D -> 2D perspective projection done here.
# Layer 1 = the gravity grid (drawn at half resolution), layer 0 = everything else.
import math
import time

import numpy as np

MAXP = 1024
GRID_N, GRID_S, EXTENT = 15, 18, 1.15
_MEM = {'sig': None, 'plan': None, 'comet': None, 'trail': [], 'local_w': {}, 'names': [], 'cam': None}


def onSetupParameters(scriptOp):
    return


def E():
    return op.Song.op('engine').module


class Prims:
    def __init__(self):
        self.a = np.zeros((3, MAXP, 4), np.float32)
        self.a[0, :, 0] = -1
        self.n = 0

    def add(self, t, ax, ay, bx, by, w, glow, alpha, rgb, layer=0):
        if self.n >= MAXP - 1 or abs(alpha) <= 0.003:
            return
        i = self.n
        self.a[0, i] = (t, ax, ay, bx)
        self.a[1, i] = (by, w, glow, alpha)
        self.a[2, i] = (rgb[0], rgb[1], rgb[2], layer)
        self.n += 1

    def line(self, a, b, w, alpha, rgb, glow=0.0, layer=0):
        if a is None or b is None:
            return
        self.add(0, a[0], a[1], b[0], b[1], w, glow, alpha, rgb, layer)

    def ring(self, c, r, w, alpha, rgb, glow=0.0):
        if c is not None:
            self.add(1, c[0], c[1], r, 0, w, glow, alpha, rgb)

    def disc(self, c, r, alpha, rgb, glow=0.0):
        if c is not None:
            self.add(2, c[0], c[1], r, 0, 0, glow, alpha, rgb)


def colour(note):
    import chartlib as cl
    try:
        return cl.hex_to_rgb(cl.color_for(note, E().palette()))
    except Exception:
        return (0.7, 0.7, 0.7)


# ---------------------------------------------------------------- the world
def key_place(key, home):
    """(x, z) of a key's star: angle = signed steps around the circle of fifths from home, radius = how far."""
    import harmony as h
    f = ((h.pc(key) - h.pc(home)) * 7) % 12
    s = f - 12 if f > 6 else f
    if s == 0:
        return 0.0, 0.0
    r = 0.22 + 0.8 * (abs(s) - 1) / 5.0
    a = s * math.pi / 6.0
    return r * math.sin(a), r * math.cos(a)


def wells(home, local):
    """[(x, z, depth, width)] gravity wells: home deepest, home's cohorts shallower, the local tonic too."""
    import journey as j
    out = [(0.0, 0.0, 0.55, 0.16)]
    cohort = set(j.minor_third_cohort(home)[1:]) | set(j.major_third_cohort(home)[1:])
    for k in cohort:
        x, z = key_place(k, home)
        out.append((x, z, 0.28, 0.12))
    for k, w in _MEM['local_w'].items():
        if w > 0.01:
            x, z = key_place(k, home)
            out.append((x, z, 0.3 * w, 0.11))
    return out


def height(x, z, W):
    y = 0.22 * (x * x + z * z)                             # the further from home, the higher the climb
    for wx, wz, d, s in W:
        y -= d * math.exp(-((x - wx) ** 2 + (z - wz) ** 2) / (s * s))
    return y


class Camera:
    """Look-at perspective camera -> figure coordinates (short side of the frame = -1..1)."""
    def __init__(self, target, dist, pitch, yaw, fov=38.0):
        self.t = target
        cp, sp = math.cos(pitch), math.sin(pitch)
        self.eye = (target[0] + dist * cp * math.sin(yaw), target[1] + dist * sp, target[2] + dist * cp * math.cos(yaw))
        f = [target[i] - self.eye[i] for i in range(3)]
        n = math.sqrt(sum(v * v for v in f))
        self.f = [v / n for v in f]
        up = (0.0, 1.0, 0.0)
        r = [self.f[1] * up[2] - self.f[2] * up[1], self.f[2] * up[0] - self.f[0] * up[2],
             self.f[0] * up[1] - self.f[1] * up[0]]
        n = math.sqrt(sum(v * v for v in r))
        self.r = [v / n for v in r]
        self.u = [self.r[1] * self.f[2] - self.r[2] * self.f[1], self.r[2] * self.f[0] - self.r[0] * self.f[2],
                  self.r[0] * self.f[1] - self.r[1] * self.f[0]]
        self.k = 1.0 / math.tan(math.radians(fov) / 2)

    def p(self, x, y, z):
        d = (x - self.eye[0], y - self.eye[1], z - self.eye[2])
        zc = sum(d[i] * self.f[i] for i in range(3))
        if zc < 0.05:
            return None
        return (self.k * sum(d[i] * self.r[i] for i in range(3)) / zc,
                self.k * sum(d[i] * self.u[i] for i in range(3)) / zc)

    def scale(self, x, y, z):
        d = (x - self.eye[0], y - self.eye[1], z - self.eye[2])
        zc = sum(d[i] * self.f[i] for i in range(3))
        return self.k / max(zc, 0.05)


def plan_for(s):
    import journey as j
    sig = (id(s), s.key)
    if _MEM['sig'] != sig:
        _MEM['sig'] = sig
        _MEM['plan'] = j.journey_plan(s)
        _MEM['local_w'] = {}
        _MEM['trail'] = []
        _MEM['comet'] = None
    return _MEM['plan']


def now_index(s):
    clk = op.Song.op('out')
    playing = clk['playing'].eval() > 0.5
    if not playing:
        return 0, False
    bar, beat, phase = int(clk['bar'].eval()), int(clk['beat'].eval()), clk['beat_phase'].eval()
    b = (bar - 1) * s.beats_per_bar + (beat - 1) + phase
    idx = 0
    for i, ev in enumerate(s.events):
        if ev[0] <= b + 1e-6:
            idx = i
        else:
            break
    return idx, True


DEGREES_FIFTHS = ['4', '1', '5', '2', '6', '3', '7']          # planets in fifths order around the star


def planet_place(star_xz, deg_index, t, r=0.11):
    a = (deg_index - 1) * (2 * math.pi / 7) + t * 0.05
    return star_xz[0] + r * math.sin(a), star_xz[1] + r * math.cos(a)


def onCook(scriptOp):
    absTime.frame
    P = Prims()
    L = parent()
    s = E().song()
    if s is None:
        _MEM['names'] = []
        scriptOp.copyNumpyArray(P.a)
        return
    import harmony as h
    import journey as j
    plan = plan_for(s)
    idx, playing = now_index(s)
    info = plan[idx]
    home = s.key
    local = info['local']
    cur = s.events[idx][2]
    nxt = s.events[(idx + 1) % len(s.events)][2]
    t = time.time()

    # local tonic weights ease in/out (a star you're orbiting deepens its valley)
    for k in list(_MEM['local_w']):
        _MEM['local_w'][k] *= 0.97
    _MEM['local_w'][local] = min(1.0, _MEM['local_w'].get(local, 0.0) * 0.97 + 0.06)
    W = wells(home, local)

    # where is the current chord? a planet of the local star if diatonic there, else a moon of the next chord
    star = key_place(local, home)
    deg = None
    for i, d in enumerate(DEGREES_FIFTHS):
        if h.pc(h.spell(local, d)) == h.pc(cur.root):
            deg = i
    if deg is not None:
        px, pz = planet_place(star, deg, t)
        is_moon = False
    else:
        tgt_deg = None
        for i, d in enumerate(DEGREES_FIFTHS):
            if h.pc(h.spell(local, d)) == h.pc(nxt.root):
                tgt_deg = i
        anchor = planet_place(star, tgt_deg, t) if tgt_deg is not None else star
        a = t * 0.8
        px, pz = anchor[0] + 0.045 * math.sin(a), anchor[1] + 0.045 * math.cos(a)
        is_moon = True
    target = (px, height(px, pz, W) + 0.04, pz)

    # comet glides to the chord
    c = _MEM['comet'] or target
    k = 0.12
    c = tuple(c[i] + (target[i] - c[i]) * k for i in range(3))
    _MEM['comet'] = c
    _MEM['trail'].append(c)
    _MEM['trail'] = _MEM['trail'][-int(max(4, L.par.Trail.eval() * 30)):]

    # camera: follow the comet, or watch from above
    follow = L.par.View.eval() == 'follow'
    tgt = (c[0] * 0.6, 0.0, c[2] * 0.6) if follow else (0.0, 0.0, 0.0)
    if _MEM['cam'] is None:
        _MEM['cam'] = tgt
    _MEM['cam'] = tuple(_MEM['cam'][i] + (tgt[i] - _MEM['cam'][i]) * 0.04 for i in range(3))
    cam = Camera(_MEM['cam'], 1.15 if follow else 2.1, math.radians(L.par.Tilt.eval()),
                 math.radians(L.par.Spin.eval()) + (t * 0.02 if L.par.Drift.eval() else 0.0))

    # ---- gravity grid (layer 1)
    if L.par.Grid.eval():
        gc = (0.35, 0.42, 0.62)
        xs = [-EXTENT + 2 * EXTENT * i / (GRID_N - 1) for i in range(GRID_N)]
        ss = [-EXTENT + 2 * EXTENT * i / (GRID_S - 1) for i in range(GRID_S)]
        for x in xs:
            prev = None
            for z in ss:
                q = cam.p(x, height(x, z, W), z)
                if prev is not None and q is not None:
                    P.line(prev, q, 0.0022, 0.55, gc, 0.0, layer=1)
                prev = q
        for z in xs:
            prev = None
            for x in ss:
                q = cam.p(x, height(x, z, W), z)
                if prev is not None and q is not None:
                    P.line(prev, q, 0.0022, 0.55, gc, 0.0, layer=1)
                prev = q

    # ---- stars: the 12 keys
    names = []
    cohort = set(j.minor_third_cohort(home)) | set(j.major_third_cohort(home))
    for pcn in range(12):
        key = j.practical_key(j.KEY_NAMES[(h.pc(home) + pcn) % 12])
        if key == j.practical_key(local):
            key = local
        x, z = key_place(key, home)
        y = height(x, z, W)
        q = cam.p(x, y + 0.012, z)
        sc = cam.scale(x, y, z)
        here = key == local
        is_home = key == home
        r = (0.016 if is_home else 0.011 if key in cohort else 0.007) * sc * 1.4
        al = 1.0 if (is_home or here) else 0.75 if key in cohort else 0.45
        P.disc(q, r * (1.4 if here else 1.0), al, colour(key), 1.4 if here else 0.6 if is_home else 0.2)
        if is_home:
            P.ring(q, r * 1.9, 0.0018, 0.6, (1.0, 0.92, 0.75), 0.3)
        if q is not None:
            names.append((q, key, 1.0 if (here or is_home) else 0.55, r))

    # ---- planets of the local star, and the current chord
    for i, d in enumerate(DEGREES_FIFTHS):
        note = h.spell(local, d)
        x, z = planet_place(star, i, t)
        y = height(x, z, W) + 0.02
        q = cam.p(x, y, z)
        sc = cam.scale(x, y, z)
        lit = (not is_moon) and i == deg
        P.disc(q, (0.009 if lit else 0.005) * sc, 1.0 if lit else 0.55, colour(note), 1.2 if lit else 0.15)
    # orbit ring (as a polygon)
    prev = None
    for i in range(37):
        a = i * 2 * math.pi / 36 + t * 0.05
        x, z = star[0] + 0.11 * math.sin(a), star[1] + 0.11 * math.cos(a)
        q = cam.p(x, height(x, z, W) + 0.02, z)
        P.line(prev, q, 0.0012, 0.25, (0.8, 0.8, 0.9))
        prev = q
    if is_moon:
        q = cam.p(px, target[1], pz)
        P.disc(q, 0.006 * cam.scale(px, target[1], pz), 1.0, colour(cur.root), 1.3)

    # ---- comet, trail, tether home
    tr = _MEM['trail']
    col = colour(cur.root)
    for i in range(1, len(tr)):
        a_, b_ = cam.p(*tr[i - 1]), cam.p(*tr[i])
        f = i / len(tr)
        P.line(a_, b_, 0.0025 * f + 0.0008, 0.8 * f, col, 0.6 * f)
    q = cam.p(*c)
    P.disc(q, 0.008 * cam.scale(*c), 1.0, (1.0, 0.97, 0.9), 1.6)
    if L.par.Tether.eval():
        tension, parts = j.tension(home, local, cur.symbol.split('/')[0], depth=info['depth'])
        f = min(1.0, tension / 6.0)
        hq = cam.p(0.0, height(0, 0, W) + 0.012, 0.0)
        tc = (0.6 + 0.4 * f, 0.75 - 0.45 * f, 0.9 - 0.65 * f)
        mid = ((c[0]) / 2, max(c[1], 0.0) + 0.06 * (1 - f), c[2] / 2)          # slack when tension is low
        m2 = cam.p(*mid)
        P.line(q, m2, 0.0012 + 0.002 * f, 0.35 + 0.5 * f, tc, 0.3 * f)
        P.line(m2, hq, 0.0012 + 0.002 * f, 0.35 + 0.5 * f, tc, 0.3 * f)
        _MEM['tension'] = (tension, parts)
    _MEM['names'] = names if L.par.Names.eval() else []
    _MEM['info'] = (info, cur, local)
    scriptOp.copyNumpyArray(P.a)
    return


def names_table(dat):
    dat.clear()
    dat.appendRow(['text', 'x', 'y'])
    W, H = op.Config.par.Width.eval(), op.Config.par.Height.eval()
    unit = min(W, H) / 2.0
    fs = min(W, H) * 0.026
    for q, name, alpha, r in _MEM['names']:
        x = W / 2 + q[0] * unit - 0.29 * fs * len(name)
        y = H / 2 + q[1] * unit + r * unit + 4
        dat.appendRow([name, round(x, 1), round(y, 1)])


def label():
    s = E().song()
    if s is None or 'info' not in _MEM:
        return ''
    info, cur, local = _MEM['info']
    t = _MEM.get('tension', (0, {}))[0]
    role = info['role'] or '—'
    where = 'home' if local == s.key else 'orbiting %s%s' % (local, ' minor' if info['minor'] else '')
    return '%s   %s      %s      %s      tension %.1f' % (s.chart['title'], cur.symbol, role, where, t)
