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
# Output: rows 0-2 = bodies (layer 0, full resolution), rows 3-5 = the gravity grid (layer 1, built with numpy,
# drawn at low resolution: it's soft background light), so each pass only loops over its own primitives.
# Protagonist (Galaxy › Protagonist): a comet, or your melody whisp (the pitch follower: each note you play
# puffs out of the traveller in its palette colour, higher for higher notes, and is left behind as a wake).
import math
import time

import numpy as np

MAXP = 2048
GRID_N, GRID_S, EXTENT = 13, 26, 1.2
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
    out = [(0.0, 0.0, 0.5, 0.26)]
    cohort = set(j.minor_third_cohort(home)[1:]) | set(j.major_third_cohort(home)[1:])
    for k in cohort:
        x, z = key_place(k, home)
        out.append((x, z, 0.2, 0.17))
    for k, w in _MEM['local_w'].items():
        if w > 0.01:
            x, z = key_place(k, home)
            out.append((x, z, 0.22 * w, 0.15))
    return out


def height(x, z, W):
    y = 0.18 * (x * x + z * z)                             # the further from home, the higher the climb
    for wx, wz, d, s in W:
        y -= d * math.exp(-((x - wx) ** 2 + (z - wz) ** 2) / (s * s))
    return y


def height_np(X, Z, W):
    Y = 0.18 * (X * X + Z * Z)
    for wx, wz, d, sg in W:
        Y = Y - d * np.exp(-((X - wx) ** 2 + (Z - wz) ** 2) / (sg * sg))
    return Y


class Camera:
    """Look-at perspective camera -> figure coordinates (short side of the frame = -1..1).
    Either orbit a target (dist, pitch, yaw) or give the eye position directly (eye=...)."""
    def __init__(self, target, dist=1.0, pitch=0.6, yaw=0.0, fov=38.0, eye=None):
        self.t = target
        cp, sp = math.cos(pitch), math.sin(pitch)
        self.eye = eye or (target[0] + dist * cp * math.sin(yaw), target[1] + dist * sp,
                           target[2] + dist * cp * math.cos(yaw))
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
        self.fov = fov

    def p(self, x, y, z):
        d = (x - self.eye[0], y - self.eye[1], z - self.eye[2])
        zc = sum(d[i] * self.f[i] for i in range(3))
        if zc < 0.05:
            return None
        return (self.k * sum(d[i] * self.r[i] for i in range(3)) / zc,
                self.k * sum(d[i] * self.u[i] for i in range(3)) / zc)

    def p_np(self, X, Y, Z):
        """Vectorised p(): (u, v, depth, valid) arrays."""
        dx, dy, dz = X - self.eye[0], Y - self.eye[1], Z - self.eye[2]
        zc = dx * self.f[0] + dy * self.f[1] + dz * self.f[2]
        ok = zc > 0.05
        zs = np.where(ok, zc, 1.0)
        u = self.k * (dx * self.r[0] + dy * self.r[1] + dz * self.r[2]) / zs
        v = self.k * (dx * self.u[0] + dy * self.u[1] + dz * self.u[2]) / zs
        return u, v, zc, ok

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
        _MEM['reset'] = True                  # a new song: the particles start again at home
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
        empty = np.zeros((3, MAXP, 4), np.float32)
        empty[0, :, 0] = -1
        scriptOp.copyNumpyArray(np.concatenate([P.a, empty], axis=0))
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

    # camera: body cam (riding just behind the traveller, looking where it's heading), follow, or from above
    view = L.par.View.eval()
    if view == 'bodycam':
        # heading = the smoothed direction of travel (kept when the traveller pauses); fall back: toward the
        # chord it's heading for, then: away from home
        prev = _MEM['trail'][-6] if len(_MEM['trail']) > 6 else c
        v = (c[0] - prev[0], c[2] - prev[2])
        n = math.hypot(*v)
        if n < 1e-3:
            v = (target[0] - c[0], target[2] - c[2])
            n = math.hypot(*v)
        if n < 1e-3:
            v, n = (c[0] or 0.001, c[2] or 0.001), math.hypot(c[0] or 0.001, c[2] or 0.001)
        hd = _MEM.get('heading') or (v[0] / n, v[1] / n)
        hd = (hd[0] + (v[0] / n - hd[0]) * 0.03, hd[1] + (v[1] / n - hd[1]) * 0.03)
        hn = math.hypot(*hd) or 1.0
        hd = (hd[0] / hn, hd[1] / hn)
        _MEM['heading'] = hd
        back, up, ahead = 0.2, 0.045 + 0.008 * math.sin(t * 1.3), 0.22
        ex_, ez_ = c[0] - hd[0] * back, c[2] - hd[1] * back
        eye = (ex_, max(height(ex_, ez_, W) + 0.03, c[1] + up), ez_)
        look = (c[0] + hd[0] * ahead, c[1] + 0.03, c[2] + hd[1] * ahead)
        # rigidly attached to the traveller (only the heading is smoothed), so it stays in the lower middle
        cam = Camera(look, eye=eye, fov=L.par.Bodycamfov.eval())
    else:
        _MEM['bc'] = None
        follow = view == 'follow'
        tgt = (c[0] * 0.6, 0.0, c[2] * 0.6) if follow else (0.0, 0.0, 0.0)
        if _MEM['cam'] is None:
            _MEM['cam'] = tgt
        _MEM['cam'] = tuple(_MEM['cam'][i] + (tgt[i] - _MEM['cam'][i]) * 0.04 for i in range(3))
        cam = Camera(_MEM['cam'], 1.7 if follow else 2.6, math.radians(L.par.Tilt.eval()),
                     math.radians(L.par.Spin.eval()) + (t * 0.02 if L.par.Drift.eval() else 0.0))

    # ---- gravity grid (layer 1, numpy)
    grid = np.zeros((3, MAXP, 4), np.float32)
    grid[0, :, 0] = -1
    if L.par.Grid.eval() and L.par.Texture.eval() == 'lines':
        lin = np.linspace(-EXTENT, EXTENT, GRID_N)
        smp = np.linspace(-EXTENT, EXTENT, GRID_S)
        segs = []
        for X, Z in (np.meshgrid(smp, lin), np.meshgrid(lin, smp, indexing='ij')):
            # rows of X/Z are lines; columns run along each line
            if X.shape[1] != GRID_S:
                X, Z = X.T, Z.T
            u, v, zc, ok = cam.p_np(X, height_np(X, Z, W), Z)
            good = ok[:, :-1] & ok[:, 1:]
            depth = 0.5 * (zc[:, :-1] + zc[:, 1:])
            alpha = np.clip(1.25 - depth / 3.2, 0.12, 1.0) * 0.6
            segs.append(np.stack([u[:, :-1][good], v[:, :-1][good], u[:, 1:][good], v[:, 1:][good],
                                  alpha[good]], axis=1))
        seg = np.concatenate(segs)[:MAXP - 1]
        n = len(seg)
        gc = (0.35, 0.42, 0.62)
        grid[0, :n, 0] = 0
        grid[0, :n, 1] = seg[:, 0]
        grid[0, :n, 2] = seg[:, 1]
        grid[0, :n, 3] = seg[:, 2]
        grid[1, :n, 0] = seg[:, 3]
        grid[1, :n, 1] = 0.0026
        grid[1, :n, 2] = 0.0
        grid[1, :n, 3] = seg[:, 4]
        grid[2, :n, 0], grid[2, :n, 1], grid[2, :n, 2] = gc

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
        r = min(r, 0.045)                                     # nothing balloons up close
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
        P.disc(q, min(0.03, (0.009 if lit else 0.005) * sc), 1.0 if lit else 0.55, colour(note), 1.2 if lit else 0.15)
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
        P.disc(q, min(0.025, 0.006 * cam.scale(px, target[1], pz)), 1.0, colour(cur.root), 1.3)

    # ---- comet, trail, tether home
    tr = _MEM['trail']
    col = colour(cur.root)
    for i in range(1, len(tr)):
        a_, b_ = cam.p(*tr[i - 1]), cam.p(*tr[i])
        f = i / len(tr)
        P.line(a_, b_, 0.0025 * f + 0.0008, 0.8 * f, col, 0.6 * f)
    q = cam.p(*c)
    if L.par.Protagonist.eval() == 'whisp':
        draw_whisp(P, cam, c, t, L)
        P.disc(q, min(0.012, 0.004 * cam.scale(*c)), 0.9, (1.0, 0.97, 0.9), 0.8)      # a small bright core
    else:
        P.disc(q, min(0.022, 0.008 * cam.scale(*c)), 1.0, (1.0, 0.97, 0.9), 1.6)
    if L.par.Tether.eval():
        tension, parts = j.tension(home, local, cur.symbol.split('/')[0], depth=info['depth'])
        f = min(1.0, tension / 6.0)
        tc = (0.6 + 0.4 * f, 0.75 - 0.45 * f, 0.9 - 0.65 * f)
        hy = height(0, 0, W) + 0.012
        prev_ = q
        for i in range(1, 13):                                # a rope: sags when slack, straight when taut
            u = i / 12.0
            x_, z_ = c[0] * (1 - u), c[2] * (1 - u)
            y_ = c[1] * (1 - u) + hy * u - 0.12 * (1 - f) * math.sin(math.pi * u)
            nq = cam.p(x_, y_, z_)
            P.line(prev_, nq, 0.0012 + 0.0022 * f, 0.35 + 0.5 * f, tc, 0.3 * f)
            prev_ = nq
        _MEM['tension'] = (tension, parts)
    _MEM['names'] = names if L.par.Names.eval() else []
    _MEM['info'] = (info, cur, local)
    _MEM['camspec'] = (cam.eye, cam.r, cam.u, cam.f, cam.fov)
    _MEM['wells'] = W
    mk = []
    for pcn in range(12):
        k_ = j.practical_key(j.KEY_NAMES[(h.pc(home) + pcn) % 12])
        x_, z_ = key_place(k_, home)
        mk.append((x_, z_, 0.012 if k_ == home else 0.009 if k_ == local else 0.005,
                   1.0 if k_ in (home, local) else 0.45, colour(k_)))
    mk.append((c[0], c[2], 0.006, 1.0, (1.0, 0.97, 0.9)))
    _MEM['marks'] = mk
    # the Attractor texture: which attractor each key area holds, where, how wild (frame_update sends it on)
    import attractors as AT
    if _MEM.get('sim_local') != local:
        _MEM['sim_local'] = local
        _MEM['epoch'] = _MEM.get('epoch', 0) + 1
    size = L.par.Attractorsize.eval()
    hx, hz = key_place(home, home)
    lx, lz = star
    tens = j.tension(home, local, cur.symbol.split('/')[0], depth=info['depth'])[0]
    _MEM['sim'] = {
        'home': (hx, height(hx, hz, W) + size * 1.1, hz, ATT_ORDER.index(AT.attractor_for(home, home))),
        'local': (lx, height(lx, lz, W) + size * 1.1, lz, ATT_ORDER.index(AT.attractor_for(home, local))),
        'tension': min(1.0, 0.15 + tens / 7.0), 'epoch': _MEM['epoch'], 'size': size,
        'homecol': colour(home), 'localcol': colour(local)}
    scriptOp.copyNumpyArray(np.concatenate([P.a, grid], axis=0))
    return


ATT_ORDER = ['lorenz', 'thomas', 'aizawa', 'dadras', 'halvorsen', 'tscus', 'fourwing']   # = gen_attractor_glsl.py


def frame_update(G):
    """Every frame (galaxy/names_tick): point the TD camera like ours, feed the particle simulation."""
    spec, sim = _MEM.get('camspec'), _MEM.get('sim')
    if spec is None or sim is None:
        return
    eye, r, u, f, fov = spec
    cam = G.op('att_cam')
    m = tdu.Matrix()
    cols = (r, u, (-f[0], -f[1], -f[2]), eye)
    for c_ in range(4):
        for r_ in range(3):
            m[r_, c_] = cols[c_][r_]
    cam.setTransform(m)
    cam.par.fov = fov
    sm = G.op('att_sim')
    sm.par.vec0valuex, sm.par.vec0valuey, sm.par.vec0valuez, sm.par.vec0valuew = sim['home']
    sm.par.vec1valuex, sm.par.vec1valuey, sm.par.vec1valuez, sm.par.vec1valuew = sim['local']
    sm.par.vec2valuex, sm.par.vec2valuey = sim['tension'], sim['epoch']
    sm.par.vec2valuez, sm.par.vec2valuew = sim['size'], G.par.Homeshare.eval()
    sm.par.vec3valuex = absTime.frame
    reset = _MEM.pop('reset', False)
    sm.par.vec3valuew = 1.0 if reset else 0.0
    cl_ = G.op('att_col')
    cl_.par.vec0valuex, cl_.par.vec0valuey, cl_.par.vec0valuez = sim['homecol']
    cl_.par.vec0valuew = G.par.Particlebright.eval()
    cl_.par.vec1valuex, cl_.par.vec1valuey, cl_.par.vec1valuez = sim['localcol']
    cl_.par.vec1valuew = G.par.Homeshare.eval()
    if G.par.Texture.eval() == 'fluid':
        fluid_update(G)


FLUID_PASSES = ('fl_vel', 'fl_dye', 'fl_wave', 'fl_view', 'fl_marksdraw')


def fluid_update(G):
    """Every frame: the traveller, its notes (pulses and pings), the current, the bed -> the fluid passes."""
    import time as _t
    sim = _MEM.get('sim')
    c = _MEM.get('comet')
    if sim is None or c is None:
        return
    span = G.par.Fluidspan.eval()
    aspect = op.Config.par.Width.eval() / max(1.0, op.Config.par.Height.eval())
    to_uv = lambda x, z: (x / (span * aspect) + 0.5, z / span + 0.5)
    tu, tv = to_uv(c[0], c[2])
    hd = _MEM.get('heading') or (0.0, 1.0)
    # notes: onset -> pulse; pings every note / only long notes / off
    a = op.Analysis.op('out')
    try:
        clar, lev, midi = a['clarity'].eval(), a['level'].eval(), a['midi'].eval()
    except Exception:
        clar, lev, midi = 0, 0, 0
    now = _t.time()
    fn = _MEM.setdefault('fnote', {'pc': None, 't0': 0.0, 'pinged': False, 'lev': 0.0})
    pulse, ping, notecol = 0.0, 0.0, None
    if clar >= G.par.Whispclarity.eval() and lev > 0.04 and midi > 0:
        pc = int(round(midi)) % 12
        onset = pc != fn['pc'] or lev > fn['lev'] * 1.6 + 0.05
        if onset:
            fn.update(pc=pc, t0=now, pinged=False)
            pulse = 1.0
        mode = G.par.Pings.eval()
        if not fn['pinged'] and (mode == 'every' and onset or mode == 'long' and now - fn['t0'] > 0.3):
            ping, fn['pinged'] = G.par.Pingsize.eval(), True
        tones = op.Song.op('tones')
        import harmony as h
        names = {h.pc(r[0].val): r[0].val for r in tones.rows()[1:]} if tones.numRows > 1 else {}
        nm = names.get(pc) or ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'][pc]
        notecol = colour(nm)
    else:
        fn['pc'] = None
    fn['lev'] = lev
    dye = notecol or tuple(0.35 * x for x in sim['localcol'])
    clk = op.Song.op('out')
    s = E().song()
    form_pos = 0.0
    if s is not None and clk['playing'].eval() > 0.5:
        form_pos = (clk['bar'].eval() - 1 + clk['bar_phase'].eval()) / max(1, s.chorus_bars)
    hu, hv = to_uv(0.0, 0.0)
    lx, lz = sim['local'][0], sim['local'][2]
    lu, lv = to_uv(lx, lz)
    cur = {'none': 0, 'home': 1, 'form': 2}[G.par.Current.eval()]
    vals = {
        'uTrav': (tu, tv, hd[0], hd[1]),
        'uInj': (G.par.Push.eval(), G.par.Dyeamount.eval() * (1.0 if notecol else 0.4), 0.035, pulse),
        'uDye': (dye[0], dye[1], dye[2], G.par.Dyedecay.eval()),
        'uFlow': (cur, G.par.Currentstrength.eval(), form_pos * 6.2831853, G.par.Viscosity.eval()),
        'uHome': (hu, hv, lu, lv),
        'uBed': (G.par.Bed.eval(), G.par.Beddrag.eval() * G.par.Bed.eval(), G.par.Wavespeed.eval(), ping),
        'uMisc': (G.par.Vorticity.eval(), aspect, now % 1000.0, G.par.Inkbright.eval()),
    }
    for name in FLUID_PASSES:
        o = G.op(name)
        for i, (un, v) in enumerate(vals.items()):
            for k, x in zip('xyzw', v):
                getattr(o.par, 'vec%dvalue%s' % (i, k)).val = x


def draw_whisp(P, cam, c, t, L):
    """The melody whisp: each note you play (pitch follower) puffs out of the traveller - palette colour of its
    spelling in the current chord-scale, higher above the traveller for higher notes - and stays where it was
    born, so the traveller leaves your line behind as a glowing wake. Consecutive notes are joined."""
    import harmony as h
    life = max(0.5, L.par.Trail.eval() * 1.6)
    a = op.Analysis.op('out')
    try:
        clarity, level, midi = a['clarity'].eval(), a['level'].eval(), a['midi'].eval()
    except Exception:
        clarity, level, midi = 0, 0, 0
    puffs = _MEM.setdefault('puffs', [])
    if clarity >= L.par.Whispclarity.eval() and level > 0.04 and midi > 0:
        pc = int(round(midi)) % 12
        last = puffs[-1] if puffs else None
        if last is None or last[6] != pc or t - last[4] > 0.12:
            tones = op.Song.op('tones')
            names = {h.pc(r[0].val): r[0].val for r in tones.rows()[1:]} if tones.numRows > 1 else {}
            name = names.get(pc) or ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'][pc]
            hd = _MEM.get('heading') or (0.0, 1.0)
            side = 0.025 * math.sin(t * 2.3)
            up = 0.015 + 0.09 * max(0.0, min(1.0, (midi - 40) / 48.0))
            puffs.append([c[0] - hd[1] * side, c[1] + up, c[2] + hd[0] * side, colour(name), t, level, pc])
    _MEM['puffs'] = [p for p in puffs if t - p[4] < life][-160:]
    prev = None
    for x, y, z, rgb, tb, lv, pc in _MEM['puffs']:
        age = (t - tb) / life
        f = (1.0 - age) ** 1.5
        y2 = y + 0.03 * age                                   # drifts up as it fades
        q = cam.p(x, y2, z)
        sc = cam.scale(x, y2, z)
        r = min(0.03, (0.004 + 0.006 * min(1.0, lv * 1.5)) * sc * (1.0 + 1.2 * age))
        P.disc(q, r, 0.9 * f, rgb, 1.4 * f)
        if prev is not None and tb - prev[1] < 0.6:
            P.line(prev[0], q, 0.0018, 0.6 * f, rgb, 0.5 * f)
        prev = (q, tb)


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
