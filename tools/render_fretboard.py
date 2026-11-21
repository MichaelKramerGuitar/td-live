"""Bird's-eye fretboard of chord-scales, to check the harmony engine and palette by eye.

    python tools/render_fretboard.py F 'I7' '#IVo7' 'ii-7'     -> docs/img/fretboard_F.png

Dot colour = palette colour of the SPELLED note; dot size = harmonic weight (root > 3rd/7th > 5th >
tensions). Strings low E at the bottom, like Michael's reference diagrams. The live landscape uses the same
data seen from the bridge.
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chartlib as cl  # noqa: E402
import harmony as h  # noqa: E402

key = sys.argv[1] if len(sys.argv) > 1 else 'F'
numerals = sys.argv[2:] or ['I7', '#IVo7', 'ii-7']
pal = cl.load_palette()
FRETS = 19

fig, axes = plt.subplots(len(numerals), 1, figsize=(12, 2.6 * len(numerals)), dpi=110)
axes = axes if len(numerals) > 1 else [axes]
for ax, num in zip(axes, numerals):
    c = h.chord(num, key)
    ax.set_facecolor('#f4efd9')
    for s in range(6):
        ax.plot([0, FRETS + 0.5], [s, s], color='#9a9a9a', lw=1 + 0.25 * (5 - s), zorder=1)
    for f in range(FRETS + 1):
        ax.plot([f + 0.5, f + 0.5], [-0.2, 5.2], color='#b9b2a0', lw=2.5 if f == 0 else 0.8, zorder=1)
    for f in (3, 5, 7, 9, 15, 17, 19):
        ax.text(f, -0.75, str(f), ha='center', fontsize=8, color='#555')
    ax.text(12, -0.75, '12', ha='center', fontsize=8, color='#555')
    for s, f, note, iv, role, w in h.fretboard(c, frets=FRETS):
        ax.scatter([f], [s], s=60 + 340 * w, color=cl.color_for(note, pal), edgecolor='#222',
                   linewidth=0.6, zorder=3)
        if role == 'root':
            ax.text(f, s, note, ha='center', va='center', fontsize=6.5, color='white', zorder=4)
    ax.set_yticks(range(6))
    ax.set_yticklabels(['E', 'A', 'D', 'G', 'B', 'E'], fontsize=8)
    ax.set_xticks([])
    ax.set_xlim(-0.6, FRETS + 0.7)
    ax.set_ylim(-1.0, 5.6)
    tones = ', '.join('%s(%s)' % (n, iv) for n, iv, *_ in c.scale_tones())
    ax.set_title('%s in %s = %s   %s: %s' % (num, key, c.symbol, c.scale.replace('_', ' '), tones),
                 loc='left', fontsize=10)
    for sp in ax.spines.values():
        sp.set_visible(False)
fig.tight_layout()
out = os.path.join(cl.ROOT, 'docs', 'img', 'fretboard_%s.png' % key.replace('#', 'sharp'))
fig.savefig(out)
print(out)
