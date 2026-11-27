# Harmony Galaxy, Fluid texture: two Script TOPs share these callbacks.
#   fl_bed   - the creek bed: the galaxy's gravity landscape (home + cohort valleys, the local key deepening, the
#              climb further out) as a height map under the water, top-down (r = height).
#   fl_marks - the 12 key stars and the traveller as marks for the view (row 0: u, v, size, alpha; row 1: rgb).
import numpy as np

BED_W, BED_H = 192, 108


def onSetupParameters(scriptOp):
    return


def W_():
    return op('world_callbacks').module


def onCook(scriptOp):
    absTime.frame
    m = W_()
    G = parent()
    aspect = op.Config.par.Width.eval() / max(1.0, op.Config.par.Height.eval())
    span = G.par.Fluidspan.eval()
    if scriptOp.name == 'fl_bed':
        Wl = m._MEM.get('wells')
        a = np.zeros((BED_H, BED_W, 4), np.float32)
        if Wl:
            u = (np.arange(BED_W) + 0.5) / BED_W
            v = (np.arange(BED_H) + 0.5) / BED_H
            X = (u[None, :] - 0.5) * span * aspect
            Z = (v[:, None] - 0.5) * span
            a[..., 0] = m.height_np(X + 0 * Z, Z + 0 * X, Wl)
        a[..., 3] = 1
        scriptOp.copyNumpyArray(a)
    else:
        marks = m._MEM.get('marks') or []
        a = np.zeros((2, 16, 4), np.float32)
        for i, (x, z, size, alpha, rgb) in enumerate(marks[:16]):
            a[0, i] = (x / (span * aspect) + 0.5, z / span + 0.5, size, alpha if G.par.Attractorview == 'stars' else 0)
            a[1, i, :3] = rgb
        scriptOp.copyNumpyArray(a)
    return
