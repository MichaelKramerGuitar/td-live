# Pitch follower (Script CHOP /project1/analysis/pitch, callbacks synced to this file).
# Follows single-note lines in real time. Not a transcriber: it gives the pitch of the strongest single note
# and how sure it is (clarity). Chords and noise come out with low clarity and are ignored downstream.
#
# Method: McLeod's normalised square difference function (NSDF) on the last ~46 ms of guitar audio, via FFT.
# Out: midi (fractional MIDI note, 0 when unsure), clarity (0..1), freq (Hz).
import numpy as np

N = 2048                     # analysis window (samples): two periods of the low E at 44.1 kHz
FMIN, FMAX = 70.0, 1300.0    # guitar range, with room
_BUF = {}                    # rolling audio buffer (module memory: storing on the op made it re-cook itself)


def onSetupParameters(scriptOp):
    return


def _nsdf_pitch(x, fs):
    x = x - x.mean()
    n = len(x)
    X = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(X * np.conj(X))[:n]
    sq = x * x
    cs = np.cumsum(sq)
    total = cs[-1]
    tau = np.arange(n)
    m = (total - np.concatenate(([0.0], cs[:-1]))) + cs[::-1][tau]   # sum of x[j]^2 + x[j+tau]^2
    nsdf = 2.0 * ac / np.maximum(m, 1e-12)
    tmin, tmax = max(2, int(fs / FMAX)), min(n - 2, int(fs / FMIN))
    # key maxima (McLeod): from lag 0, skip the first positive lobe, then take the highest point of each positive
    # lobe; pick the first lobe peak >= 0.9 x the best one (avoids octave-low errors)
    zc_down = np.where((nsdf[:-1] > 0) & (nsdf[1:] <= 0))[0]
    if not zc_down.size:
        return 0.0, 0.0
    i, peaks = zc_down[0] + 1, []
    while i < tmax:
        up = np.where((nsdf[i:tmax][:-1] <= 0) & (nsdf[i:tmax][1:] > 0))[0]
        if not up.size:
            break
        a0 = i + up[0] + 1
        down = np.where((nsdf[a0:tmax][:-1] > 0) & (nsdf[a0:tmax][1:] <= 0))[0]
        a1 = a0 + down[0] + 1 if down.size else tmax
        k = a0 + int(np.argmax(nsdf[a0:a1]))
        if tmin <= k < tmax:
            peaks.append(k)
        i = a1
    if not peaks:
        return 0.0, 0.0
    best = max(nsdf[k] for k in peaks)
    k = next(k for k in peaks if nsdf[k] >= 0.9 * best)
    seg, tmin = nsdf, 0
    a, b, c = seg[k - 1], seg[k], seg[k + 1]
    den = a - 2 * b + c
    shift = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
    period = tmin + k + shift
    return fs / period, float(b)


def onCook(scriptOp):
    src = op.Sources.op('guitar')
    buf = _BUF.get(scriptOp.path)
    if buf is None or len(buf) != N:
        buf = np.zeros(N, np.float32)
    if src is not None and src.numChans:
        new = np.asarray(src.chans()[0].vals, np.float32)
        if new.size >= N:
            buf = new[-N:].copy()
        elif new.size:
            buf = np.concatenate((buf[new.size:], new))
    _BUF[scriptOp.path] = buf
    fs = src.rate if src is not None else 44100.0
    rms = float(np.sqrt(np.mean(buf * buf)))
    freq, clarity = (0.0, 0.0)
    if rms > parent().par.Pitchgate.eval():
        freq, clarity = _nsdf_pitch(buf.astype(np.float64), fs)
    midi = 69 + 12 * np.log2(freq / 440.0) if freq > 0 else 0.0
    scriptOp.clear()
    scriptOp.numSamples = 1
    for name, v in (('midi', midi), ('clarity', clarity), ('freq', freq)):
        scriptOp.appendChan(name)[0] = float(v)
    return
