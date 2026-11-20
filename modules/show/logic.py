# Show logic: the Rehearse / Record state machine.  (Text DAT /project1/show/logic, synced to this file.)
#
#   idle --start()--> countdown --(Countdown seconds)--> running --stop()--> idle
#
# `kind` is 'rehearse' or 'record'. Only 'record' writes a take. Space bar = toggle(): start the armed kind,
# or stop whatever is counting down / running. Everyone calls these functions: the parameter pulses
# (actions), the Space key (keys), the panel buttons (buttons) and the per-frame clock (tick).
import datetime
import math
import os


def S():
    return op.Show


def state():
    return S().fetch('state', 'idle')


def kind():
    return S().fetch('kind', S().par.Armed.eval())


def start(k=None):
    s = S()
    if state() != 'idle':
        return
    k = k or s.par.Armed.eval()
    s.par.Armed = k
    s.store('kind', k)
    s.store('t_go', absTime.seconds + max(0, s.par.Countdown.eval()))
    s.store('state', 'countdown')


def stop():
    s = S()
    if state() == 'running' and kind() == 'record':
        _record(False)
    s.store('state', 'idle')


def toggle():
    if state() == 'idle':
        start()
    else:
        stop()


def _record(on):
    rec = op.Output.op('recorder')
    if not on:
        rec.par.record = False
        return
    folder = os.path.join(project.folder, op.Config.par.Takesfolder.eval())
    os.makedirs(folder, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    mode = S().par.Mode.eval()
    name = '%s/%s_%s_%s.mov' % (op.Config.par.Takesfolder.eval(), stamp, mode, op.Config.par.Preset.eval())
    rec.par.file = name                       # name the take FIRST ...
    S().store('lasttake', name)
    run("op.Output.op('recorder').par.record = True", delayFrames=1)   # ... then start (never overwrites)


def _clock(secs):
    return '%d:%02d' % (int(secs // 60), int(secs % 60))


def tick():
    """Every frame: advance the countdown, update the overlay text (preview only) and Status."""
    s = S()
    st, now = state(), absTime.seconds
    k = kind()
    big, small = '', ''
    if st == 'countdown':
        left = s.fetch('t_go', now) - now
        if left <= 0:
            s.store('state', 'running')
            s.store('t_start', now)
            if k == 'record':
                _record(True)
            st = 'running'
        else:
            big = str(int(math.ceil(left)))
            small = ('REC in' if k == 'record' else 'REHEARSE in')
    if st == 'running':
        t = now - s.fetch('t_start', now)
        small = ('● REC  ' if k == 'record' else 'REHEARSE  ') + _clock(t)
    if st == 'idle':
        small = 'Space: start %s' % s.par.Armed.eval()
    ov = op.Output
    ov.op('count_text').par.text = big
    ov.op('status_text').par.text = small
    rec = (k == 'record' and st != 'idle')
    ov.op('status_text').par.fontcolorr = 1.0
    ov.op('status_text').par.fontcolorg = 0.35 if rec else 1.0
    ov.op('status_text').par.fontcolorb = 0.35 if rec else 1.0
    lvl = op.Analysis.op('out')['level']
    s.par.Status = '%s | %s | %s | input %3d%% | %s' % (
        st.upper() if st != 'running' else (k.upper()), s.par.Mode.eval(), op.Config.par.Preset.eval(),
        int((lvl.eval() if lvl is not None else 0) * 100),
        os.path.basename(s.fetch('lasttake', '')) or 'no takes yet')
