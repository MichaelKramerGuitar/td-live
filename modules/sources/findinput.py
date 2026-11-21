# Find Guitar Input (Text DAT /project1/sources/findinput, synced to this file).
# Listens to EVERY input of the audio interface for a few seconds while you play, then sets
# Config > Guitar Inputs to the input(s) that carried the guitar. Started by Config > Find Guitar Input.
SECONDS = 6.0


def start():
    S = op.Sources
    scan = S.op('scan_in')
    scan.par.active = True
    S.store('scan_peak', {})
    S.store('scan_until', absTime.seconds + SECONDS)
    op.Config.par.Inputinfo = 'Listening on all inputs... play now (%d s)' % SECONDS
    op.Show.op('logic').module.later(_step, 1)


def _step():
    S = op.Sources
    scan = S.op('scan_in')
    peaks = S.fetch('scan_peak', {})
    for i, c in enumerate(scan.chans()):
        m = max((abs(v) for v in c.vals), default=0.0)
        peaks[i + 1] = max(peaks.get(i + 1, 0.0), m)
    S.store('scan_peak', peaks)
    if absTime.seconds < S.fetch('scan_until', 0):
        op.Show.op('logic').module.later(_step, 1)
        return
    scan.par.active = False
    _finish(peaks)


def _finish(peaks):
    if not peaks:
        op.Config.par.Inputinfo = 'No inputs found on the audio device.'
        return
    best = max(peaks.values())
    if best < 0.01:
        op.Config.par.Inputinfo = 'Nothing louder than the noise floor (max %.4f). Play harder / check the interface gain.' % best
        return
    chosen = sorted(i for i, v in peaks.items() if v >= best * 0.35)[:2]
    op.Config.par.Guitarchans = ' '.join(str(i) for i in chosen)
    loud = ', '.join('%d: %.2f' % (i, peaks[i]) for i in sorted(peaks, key=peaks.get, reverse=True)[:4])
    op.Config.par.Inputinfo = 'Guitar on input %s  (loudest: %s)' % (' + '.join(map(str, chosen)), loud)
