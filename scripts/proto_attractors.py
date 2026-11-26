"""Offline prototype for the Galaxy's Attractor texture: contact sheets as PNGs (no TouchDesigner needed).
    python3 scripts/proto_attractors.py OUTDIR
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import attractors as A  # noqa: E402
import chartlib as cl  # noqa: E402
import harmony  # noqa: E402
cl.harmony = harmony

PAL = cl.load_palette() if hasattr(cl, 'load_palette') else None


def rgb(note):
    import yaml
    pal = PAL or yaml.safe_load(open(os.path.join(ROOT, 'synesthesia', 'palette.yaml')))
    return np.array(cl.hex_to_rgb(cl.color_for(note, pal)))


def rot(P, az, el):
    ca, sa, ce, se = np.cos(az), np.sin(az), np.cos(el), np.sin(el)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    x1, y1 = ca * x - sa * y, sa * x + ca * y
    return np.stack([x1, ce * y1 - se * z, se * y1 + ce * z], -1)


VIEW = {'lorenz': (0.0, -1.5708), 'thomas': (0.7, 0.6), 'aizawa': (0.3, -1.1), 'dadras': (0.5, -0.9),
        'halvorsen': (0.8, 0.55), 'tscus': (0.6, -1.2), 'fourwing': (0.5, 0.7)}


def splat(img, P, col, size, weight=1.0, scale=0.42, centre=(0.5, 0.5)):
    """Accumulate points (normalised coords, x right / y up) into a float image as light."""
    h, w = img.shape[:2]
    u = ((P[..., 0] * scale + centre[0]) * w).astype(int).ravel()
    v = ((-P[..., 1] * scale + centre[1]) * h).astype(int).ravel()
    ok = (u >= 0) & (u < w) & (v >= 0) & (v < h)
    acc = np.zeros((h, w))
    np.add.at(acc, (v[ok], u[ok]), weight)
    for k in range(3):
        img[..., k] += acc * col[k]


def tone(img, gain):
    out = 1.0 - np.exp(-img * gain)
    return (np.clip(out, 0, 1) ** 0.85 * 255).astype(np.uint8)


def label(im, text, xy, size=18):
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype('DejaVuSans.ttf', size)
    except OSError:
        f = ImageFont.load_default()
    d.text(xy, text, fill=(190, 192, 200), font=f)


def sheet_tension(out, cell=360):
    names = list(A.ATTRACTORS)
    tens = [(0.15, 'near home (calm)'), (0.55, 'travelling'), (1.0, 'far away (wild)')]
    W, H = cell * len(tens), cell * len(names)
    big = Image.new('RGB', (W, H + 40), (0, 0, 0))
    col = rgb('Ab')
    for r, name in enumerate(names):
        az, el = VIEW[name]
        for c, (t, tl) in enumerate(tens):
            S = A.sample(name, n=2500, steps=900, tension=t, keep=260, seed=r)
            img = np.zeros((cell, cell, 3))
            splat(img, rot(S, az, el), col * 0.5 + 0.5 * np.array([1, 1, 1]) * 0.15, cell)
            im = Image.fromarray(tone(img, 0.08))
            big.paste(im, (c * cell, r * cell + 40))
            role = [k for k, v in A.ROLES.items() if v == name]
            label(big, '%s%s  -  %s' % (name.capitalize(), ' [%s]' % role[0] if role else '', tl),
                  (c * cell + 10, r * cell + 48), 15)
    label(big, 'Attractors by role, calm -> wild (Lorenz: calm below 0.3, fully wild from 0.3)', (10, 10))
    big.save(os.path.join(out, 'attractors_tension.png'))


# ---------------------------------------------------------------- the journey: particles streaming key to key
def key_place(key, home):
    import harmony as h
    f = ((h.pc(key) - h.pc(home)) * 7) % 12
    s = f - 12 if f > 6 else f
    if s == 0:
        return np.array([0.0, 0.0, 0.0])
    r = 0.22 + 0.8 * (abs(s) - 1) / 5.0
    a = s * np.pi / 6.0
    return np.array([r * np.sin(a), 0.0, r * np.cos(a)])


def journey(chart_id, key, bars_to_show, out, n=3000, frames_per_bar=40, size=0.2, home_share=0.25,
            with_stars=True, tag='', style='both', trail_len=24):
    """Particles in one attractor per key area (by role: attractors.ROLES), streaming key to key; a share always
    stays on home's calm orbit. style: 'points', 'trails' or 'both'."""
    import formclock as fc
    import journey as J
    s = fc.Song(cl.load_chart(os.path.join(ROOT, 'charts', chart_id + '.yaml')), key=key)
    plan = J.journey_plan(s)
    per_bar = {}
    for ev, p in zip(s.events, plan):
        per_bar.setdefault(ev[6], (p, ev[2]))
    rng = np.random.default_rng(1)
    home_att = A.attractor_for(key, key)
    for nm in A.ATTRACTORS:
        A.norm(nm)
    seeds = {nm: (A._SEEDS[nm] - A._NORM[nm][0]) / A._NORM[nm][1] for nm in A.ATTRACTORS}
    hstep = {nm: A.ATTRACTORS[nm][1] * A._NORM[nm][2] / A._NORM[nm][1] for nm in A.ATTRACTORS}
    U = seeds[home_att][rng.integers(0, len(seeds[home_att]), n)].copy()
    homebound = np.arange(n) < int(n * home_share)
    captured = np.ones(n, bool)
    hist, shots = [], {}
    keys12 = [J.practical_key(J.KEY_NAMES[(cl.harmony.pc(key) + i) % 12]) for i in range(12)]
    last_local, att = key, home_att
    centre = np.tile(key_place(key, key), (n, 1))
    X = centre + U * size
    for bar in range(1, s.chorus_bars + 1):
        p, chord = per_bar[bar]
        local = p['local']
        tension, _ = J.tension(key, local, chord.symbol.split('/')[0], depth=p['depth'])
        tn = min(1.0, 0.15 + tension / 7.0)
        if local != last_local:
            captured[~homebound] = False
            last_local, att = local, A.attractor_for(key, local)
        pa, ph = key_place(local, key), key_place(key, key)
        centre = np.where(homebound[:, None], ph, pa)
        for fr in range(frames_per_bar):
            for _ in range(3):
                U = (X - centre) / size
                d = np.linalg.norm(U, axis=1)
                arrive = (~captured) & (d < 1.0)
                if arrive.any():
                    U[arrive] = seeds[att][rng.integers(0, len(seeds[att]), arrive.sum())] * 0.9
                    captured[arrive] = True
                V = np.zeros_like(U)
                hb = captured & homebound
                tr = captured & ~homebound
                if hb.any():
                    V[hb] = A.field_u(home_att, U[hb], 0.2) * hstep[home_att]
                if tr.any():
                    V[tr] = A.field_u(att, U[tr], tn) * hstep[att]
                st = ~captured
                if st.any():
                    to = -U[st] / (d[st, None] + 1e-6)
                    swirl = np.stack([-to[:, 2], np.zeros(st.sum()), to[:, 0]], 1)
                    V[st] = 0.012 * (2.5 * (to + 0.5 * swirl) + rng.normal(0, 0.4, (st.sum(), 3)))
                U = U + 1.6 * V
                bad = captured & ((np.linalg.norm(U, axis=1) > 3.5) | ~np.isfinite(U).all(1))
                if bad.any():
                    which = np.where(homebound[bad], home_att, att)
                    for nm in set(which):
                        idx = np.where(bad)[0][which == nm]
                        U[idx] = seeds[nm][rng.integers(0, len(seeds[nm]), len(idx))]
                X = centre + U * size
            hist.append(X.copy())
            hist = hist[-trail_len:]
        if bar in bars_to_show:
            shots[bar] = (np.array(hist), local, chord.symbol, p['role'], tension, att)
    cell, cols = 560, 3
    rows = (len(bars_to_show) + cols - 1) // cols
    big = Image.new('RGB', (cell * cols, cell * rows + 46), (0, 0, 0))
    for i, bar in enumerate(bars_to_show):
        T, local, sym, role, tension, attname = shots[bar]
        img = np.zeros((cell, cell, 3))
        pa, ph = key_place(local, key), key_place(key, key)
        mid = (pa + ph) / 2
        zoom = 0.42 / max(0.42, np.linalg.norm(pa - ph) / 2 + 0.3)

        def view(P3):
            Q = (P3 - mid)[..., [0, 2, 1]] * np.array([1, -1, 1])
            return rot(Q, 0.0, -0.55)
        Vh = view(T)                                         # (frames, n, 2/3)
        cols_ = [(homebound, rgb(key) * 0.7), (~homebound, rgb(local))]
        for mask, col in cols_:
            if style in ('trails', 'both'):
                L = len(Vh)
                for k in range(1, L):                        # segments, 4 samples each, fading with age
                    a_, b_ = Vh[k - 1][mask], Vh[k][mask]
                    w = (k / L) ** 1.5 * (0.5 if style == 'both' else 1.0)
                    for f in (0.0, 0.25, 0.5, 0.75):
                        splat(img, (a_ + (b_ - a_) * f)[None], col, cell, weight=w, scale=zoom)
            if style in ('points', 'both'):
                last = Vh[-1][mask]
                for dx in (0.0, 0.6 / (cell * zoom)):
                    for dy in (0.0, 0.6 / (cell * zoom)):
                        splat(img, (last + np.array([dx, dy, 0]))[None], col, cell,
                              weight=6.0 if style == 'points' else 4.0, scale=zoom)
        im = Image.fromarray(tone(img, 0.035 if style != 'points' else 0.06))
        if with_stars:
            d = ImageDraw.Draw(im)
            for k in keys12:
                q = view(key_place(k, key)[None])[0]
                u, v = (q[0] * zoom + 0.5) * cell, (-q[1] * zoom + 0.5) * cell
                col = tuple(int(255 * x) for x in rgb(k))
                rr = 4 if k in (key, local) else 2.5
                d.ellipse([u - rr, v - rr, u + rr, v + rr], outline=col, width=2)
                label(im, k, (u + 7, v + 4), 13)
        ox, oy = (i % cols) * cell, (i // cols) * cell + 46
        big.paste(im, (ox, oy))
        label(big, 'bar %d   %s   %s   (%s: %s)   tension %.1f' % (bar, sym, role or '', local, attname, tension),
              (ox + 10, oy + 8), 15)
    label(big, '%s in %s - one attractor per role - %s%s' % (s.chart['title'], key, style,
                                                             ', with the stars' if with_stars else ', abstract'),
          (10, 10))
    big.save(os.path.join(out, 'journey_%s_%s%s.png' % (chart_id, style, tag)))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    what = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if what in ('all', 'tension'):
        sheet_tension(out)
    if what in ('all', 'journey'):
        for style in ('points', 'trails', 'both'):
            journey('all_the_things_you_are', 'Ab', [4, 7, 12, 16, 23, 30], out, style=style)
        journey('along_came_betty', 'Ab', [3, 5, 7, 10, 17, 25], out, style='both', with_stars=False, tag='_abstract')
    print('ok')
