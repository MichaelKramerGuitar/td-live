"""Strange attractors for the Harmony Galaxy's Attractor texture (harmony-journey/TEXTURES.md).

Equations and parameter values as listed by Juan Carlos Ponce Campuzano, "Strange Attractors"
(dynamicmath.xyz/strange-attractors), implemented here from the maths (no code copied). Originally:
Lorenz (1963), Thomas (1999), Langford/Aizawa, Dadras & Momeni (2009), Halvorsen (via Sprott, Elegant Chaos).

Each attractor is normalised (centre, radius, typical speed) so they share one scale (u = (x - centre) / radius,
unit typical speed), and gets a TENSION knob that blends two flows:
    v(u) = tension * attractor(u) + (1 - tension) * calm(u)
calm = a quiet laminar orbit (a ring the particles circle smoothly): home is settled but alive;
tension 1 = the full strange attractor; in between the orbit frays into chaos.

    import attractors as A
    pts = A.sample('halvorsen', n=3000, steps=1500, tension=0.8)   # (steps, n, 3), normalised
"""
import numpy as np


def lorenz(x, y, z, s=10.0, r=28.0, b=8.0 / 3.0):
    return s * (y - x), x * (r - z) - y, x * y - b * z


def thomas(x, y, z, b=0.208186):
    return np.sin(y) - b * x, np.sin(z) - b * y, np.sin(x) - b * z


def aizawa(x, y, z, a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1):
    return ((z - b) * x - d * y,
            d * x + (z - b) * y,
            c + a * z - z ** 3 / 3.0 - (x * x + y * y) * (1 + e * z) + f * z * x ** 3)


def dadras(x, y, z, a=3.0, b=2.7, c=1.7, d=2.0, e=9.0):
    return y - a * x + b * y * z, c * y - x * z + z, d * x * y - e * z


def halvorsen(x, y, z, a=1.89):
    return (-a * x - 4 * y - 4 * z - y * y,
            -a * y - 4 * z - 4 * x - z * z,
            -a * z - 4 * x - 4 * y - x * x)


# name: (field, native dt, a start point on the attractor)
ATTRACTORS = {
    'lorenz': (lorenz, 0.004, (1.0, 1.0, 20.0)),
    'thomas': (thomas, 0.04, (1.1, 1.1, -0.01)),
    'aizawa': (aizawa, 0.008, (0.1, 0.0, 0.0)),
    'dadras': (dadras, 0.004, (1.1, 2.1, -2.0)),
    'halvorsen': (halvorsen, 0.004, (-1.48, -1.51, 2.04)),
}
_NORM = {}
_SEEDS = {}


def rk4(f, P, dt):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    k1 = np.stack(f(x, y, z), 1)
    q = P + 0.5 * dt * k1
    k2 = np.stack(f(q[:, 0], q[:, 1], q[:, 2]), 1)
    q = P + 0.5 * dt * k2
    k3 = np.stack(f(q[:, 0], q[:, 1], q[:, 2]), 1)
    q = P + dt * k3
    k4 = np.stack(f(q[:, 0], q[:, 1], q[:, 2]), 1)
    return P + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def norm(name):
    """(centre, radius, mean speed) of the attractor, from one long run (cached)."""
    if name not in _NORM:
        f, dt, start = ATTRACTORS[name]
        P = np.array([start], float)
        pts, sp = [], []
        for i in range(40000):
            P = rk4(f, P, dt)
            if i > 4000:
                pts.append(P[0].copy())
                if i % 10 == 0:
                    sp.append(np.linalg.norm(np.stack(f(*P[0]))))
        pts = np.array(pts)
        c = pts.mean(0)
        R = np.percentile(np.linalg.norm(pts - c, axis=1), 95)
        _NORM[name] = (c, R, float(np.mean(sp)))
        _SEEDS[name] = pts[::7]                    # points on the attractor: spawn / respawn particles here
    return _NORM[name]


def calm(U):
    """A quiet laminar orbit: circle the z axis at radius 0.45, drift back to the plane."""
    x, y, z = U[:, 0], U[:, 1], U[:, 2]
    r = np.sqrt(x * x + y * y) + 1e-6
    pull = 1.5 * (0.45 - r) / r
    return np.stack([-y + pull * x, x + pull * y, -1.5 * z], 1)


def field_u(name, U, tension):
    """Velocity in normalised space (u = (x - centre) / radius, unit typical speed)."""
    f, dt, start = ATTRACTORS[name]
    c, R, speed = norm(name)
    X = c + R * U
    v = np.stack(f(X[:, 0], X[:, 1], X[:, 2]), 1) / speed
    return tension * v + (1.0 - tension) * calm(U)


def sample(name, n=2000, steps=1200, tension=1.0, keep=400, seed=0):
    """Positions of n particles over the last `keep` steps, normalised (centre 0, radius ~1): (keep, n, 3)."""
    f, dt, start = ATTRACTORS[name]
    c, R, speed = norm(name)
    h = dt * speed / R                              # the native step, in normalised time
    rng = np.random.default_rng(seed)
    seeds = (_SEEDS[name] - c) / R
    U = seeds[rng.integers(0, len(seeds), n)] + rng.normal(0, 0.05, (n, 3))
    out = []
    for i in range(steps):
        k1 = field_u(name, U, tension)
        k2 = field_u(name, U + 0.5 * h * k1, tension)
        k3 = field_u(name, U + 0.5 * h * k2, tension)
        k4 = field_u(name, U + h * k3, tension)
        U = U + h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        bad = ~np.isfinite(U).all(1) | (np.linalg.norm(U, axis=1) > 4)
        if bad.any():                              # escaped (quadratic attractors can): respawn on the attractor
            U[bad] = seeds[rng.integers(0, len(seeds), bad.sum())]
        if i >= steps - keep:
            out.append(U.copy())
    return np.array(out)
