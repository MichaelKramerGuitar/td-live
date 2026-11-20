"""Render the palette's starting colours as soft fields on the circle of fifths, for tuning by eye.

    python tools/render_palette.py            -> docs/img/palette.png

Enharmonic spellings share a position on the circle (same sound) but get their own field (different colour):
sharps sit just outside the ring, flats just inside.
"""
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as cl  # noqa: E402

N = 1400
pal = cl.load_palette()
img = np.zeros((N, N, 3)) + np.array([0.20, 0.20, 0.21])
yy, xx = np.mgrid[0:N, 0:N] / N
rng = np.random.default_rng(7)
labels = []

for name, entry in pal['colors'].items():
    k = cl.fifths_index(name)
    acc = cl.parse_spelled(name)[1]
    r = 0.36 + (0.055 if acc == '#' else -0.055 if acc == 'b' else 0.0)
    a = 2 * math.pi * k / 12
    cx, cy = 0.5 + r * math.sin(a), 0.5 - r * math.cos(a)
    col = np.array(cl.hex_to_rgb(entry['start']))
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    w = np.exp(-d2 / (2 * 0.045 ** 2))                       # soft, airy field
    w *= 0.85 + 0.15 * rng.random((N, N))                     # a little grain
    img = img * (1 - 0.9 * w[..., None]) + col * (0.9 * w[..., None])
    labels.append((cx, cy, name, entry['description']))

fig = plt.figure(figsize=(9, 9), dpi=N / 9)
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(np.clip(img, 0, 1), extent=(0, 1, 1, 0))
for cx, cy, name, _ in labels:
    ax.text(cx, cy, name, color='white', ha='center', va='center', fontsize=12, alpha=0.85,
            fontweight='bold')
ax.text(0.5, 0.5, 'starting colours\ntune by eye in TD', color="#ccd", ha='center', va='center', fontsize=11)
ax.set_xlim(0, 1)
ax.set_ylim(1, 0)
ax.axis('off')
out = os.path.join(cl.ROOT, 'docs', 'img', 'palette.png')
fig.savefig(out)
print(out)
