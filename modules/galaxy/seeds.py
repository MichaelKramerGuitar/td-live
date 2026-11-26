# Harmony Galaxy, Attractor texture: the seeds TOP (Script TOP callbacks). 4096 normalised points on each
# attractor (row = attractor id, order as in scripts/gen_attractor_glsl.py), loaded from attractor_seeds.npy.
import os

import numpy as np


def onSetupParameters(scriptOp):
    return


def onCook(scriptOp):
    S = np.load(os.path.join(project.folder, 'modules', 'galaxy', 'attractor_seeds.npy'))   # (7, 4096, 3)
    a = np.zeros((S.shape[0], S.shape[1], 4), np.float32)
    a[..., :3] = S
    a[..., 3] = 1.0
    scriptOp.copyNumpyArray(a)
    return
