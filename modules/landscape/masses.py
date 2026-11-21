# Script TOP callbacks shared by landscape/masses and landscape/mass_colors.
# One pixel per fretboard position of the current chord-scale (from op.Song.op('positions')):
#   masses      = (string, y, weight, 1)   y = distance from the nut as a fraction of the scale length
#   mass_colors = (r, g, b, weight)        palette colour of the spelled note
# Open strings sit just behind the nut (y = -0.02); fretted notes sit midway between their frets.
import numpy as np


def fret_y(n):
    return 1.0 - 2.0 ** (-n / 12.0)


def onSetupParameters(scriptOp):
    return


def onCook(scriptOp):
    pos = op.Song.op('positions')
    flip = parent().par.Flip.eval()
    rows = [r for r in pos.rows()[1:]] if pos.numRows > 1 else []
    n = max(1, len(rows))
    a = np.zeros((1, n, 4), np.float32)
    for i, r in enumerate(rows):
        s, f, w = float(r[0].val), int(r[1].val), float(r[4].val)
        y = -0.02 if f == 0 else 0.5 * (fret_y(f - 1) + fret_y(f))
        if flip:
            s = 5.0 - s
        if scriptOp.name == 'masses':
            a[0, i] = (s, y, w, 1.0)
        else:
            a[0, i] = (float(r[5].val), float(r[6].val), float(r[7].val), w)
    scriptOp.copyNumpyArray(a)
    return
