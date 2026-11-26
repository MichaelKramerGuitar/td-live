"""Generate modules/galaxy/attractor_sim.frag from tools/attractors.py (the same normalisation the prototype uses).
    python3 scripts/gen_attractor_glsl.py
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import attractors as A  # noqa: E402

ORDER = ['lorenz', 'thomas', 'aizawa', 'dadras', 'halvorsen', 'tscus', 'fourwing']
FIELDS = {
    'lorenz': 'vec3(10.0 * (X.y - X.x), X.x * (28.0 - X.z) - X.y, X.x * X.y - (8.0 / 3.0) * X.z)',
    'thomas': 'vec3(sin(X.y) - 0.208186 * X.x, sin(X.z) - 0.208186 * X.y, sin(X.x) - 0.208186 * X.z)',
    'aizawa': ('vec3((X.z - 0.7) * X.x - 3.5 * X.y, 3.5 * X.x + (X.z - 0.7) * X.y, '
               '0.6 + 0.95 * X.z - X.z * X.z * X.z / 3.0 - (X.x * X.x + X.y * X.y) * (1.0 + 0.25 * X.z) '
               '+ 0.1 * X.z * X.x * X.x * X.x)'),
    'dadras': 'vec3(X.y - 3.0 * X.x + 2.7 * X.y * X.z, 1.7 * X.y - X.x * X.z + X.z, 2.0 * X.x * X.y - 9.0 * X.z)',
    'halvorsen': ('vec3(-1.89 * X.x - 4.0 * X.y - 4.0 * X.z - X.y * X.y, -1.89 * X.y - 4.0 * X.z - 4.0 * X.x - X.z * X.z, '
                  '-1.89 * X.z - 4.0 * X.x - 4.0 * X.y - X.x * X.x)'),
    'tscus': 'vec3(32.48 * (X.y - X.x) + 0.13 * X.x * X.z, 45.84 * X.x - X.x * X.z + 14.7 * X.y, 1.18 * X.z + X.x * X.y - 0.57 * X.x * X.x)',
    'fourwing': 'vec3(0.2 * X.x + X.y * X.z, 0.01 * X.x - 0.4 * X.y - X.x * X.z, -X.z - X.x * X.y)',
}


def main():
    norms = {n: A.norm(n) for n in ORDER}
    lines = []
    for i, n in enumerate(ORDER):
        c, R, sp = norms[n]
        dt = A.ATTRACTORS[n][1]
        lines.append('    if (id == %d) { vec3 X = vec3(%.6f, %.6f, %.6f) + %.6f * U; return %s / %.6f; }  // %s'
                     % (i, c[0], c[1], c[2], R, FIELDS[n], sp, n))
    hsteps = ', '.join('%.6f' % (A.ATTRACTORS[n][1] * norms[n][2] / norms[n][1]) for n in ORDER)
    src = open(os.path.join(ROOT, 'modules', 'galaxy', 'attractor_sim.frag.in')).read()
    src = src.replace('//@FIELDS', '\n'.join(lines)).replace('/*@HSTEPS*/', hsteps)
    open(os.path.join(ROOT, 'modules', 'galaxy', 'attractor_sim.frag'), 'w').write(src)
    # seeds: 4096 normalised points on each attractor (one row per attractor, in ORDER), for the seeds TOP
    import numpy as np
    rows = []
    for n in ORDER:
        c, R, sp = norms[n]
        pts = (A._SEEDS[n] - c) / R
        idx = np.linspace(0, len(pts) - 1, 4096).astype(int)
        rows.append(pts[idx])
    np.save(os.path.join(ROOT, 'modules', 'galaxy', 'attractor_seeds.npy'), np.array(rows, np.float32))
    print('ok', len(ORDER))


if __name__ == '__main__':
    main()
