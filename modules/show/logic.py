# Show logic: the Rehearse / Record state machine.  (Text DAT /project1/show/logic, synced to this file.)
#
#   idle --start()--> countdown --(Countdown seconds)--> running --stop()--> idle
#
# With a chart picked in op.Song, the countdown is a musical count-in (Song › Count-in Bars at the tempo) that
# ends exactly on the downbeat of bar 1, and the song engine follows the form from there. With Chart = none,
# the countdown is Show › Countdown seconds.
#
# `kind` is 'rehearse' or 'record'. Only 'record' writes a take. Space bar = toggle(): start the armed kind,
# or stop whatever is counting down / running. Everyone calls these functions: the parameter pulses
# (actions), the Space key (keys), the panel buttons (buttons) and the per-frame clock (tick).
import datetime
import math
import os


def S():
    return op.Show


# Small jobs to run a few frames later. TD's own delayed run counts TIMELINE frames, so it never fires while the
# timeline is paused (Space in the network editor pauses it) - which once silently stopped takes from starting.
# These run from show/tick instead, every frame no matter what.
_LATER = []


def later(fn, frames=1):
    _LATER.append([frames, fn])


def _run_later():
    for job in list(_LATER):
        job[0] -= 1
        if job[0] <= 0:
            _LATER.remove(job)
            try:
                job[1]()
            except Exception as e:
                debug('later job failed: %s' % e)


def E():
    return op.Song.op('engine').module


def PB():
    return op.Show.op('playback').module


def state():
    return S().fetch('state', 'idle')


def kind():
    return S().fetch('kind', S().par.Armed.eval())


def start(k=None):
    s = S()
    if state() != 'idle':
        return
    PB().stop()                                        # starting a take or rehearsal ends playback
    k = k or s.par.Armed.eval()
    s.par.Armed = k
    s.store('kind', k)
    count = E().count_in_seconds()
    if count is None:
        count = max(0, s.par.Countdown.eval())
    s.store('t_go', absTime.seconds + count)           # t_go = downbeat of bar 1
    s.store('state', 'countdown')


def stop():
    s = S()
    if state() == 'running' and kind() == 'record':
        _record(False)
        later(lambda: op.Show.op('playback').module.select_newest(), 30)   # the take just made
    s.store('state', 'idle')


def toggle():
    if state() == 'idle' and PB().playing():
        PB().stop()
    elif state() == 'idle':
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
    later(lambda: setattr(op.Output.op('recorder').par, 'record', True), 1)   # ... then start (never overwrites)


def _clock(secs):
    return '%d:%02d' % (int(secs // 60), int(secs % 60))


def tick():
    """Every frame: advance the countdown, drive the song engine, update overlay text (preview only), Status."""
    _run_later()
    if not op('/').time.play:                          # keep the timeline running (Space in the editor pauses it)
        op('/').time.play = True
    s = S()
    st, now = state(), absTime.seconds
    k = kind()
    big, small = '', ''
    if st == 'countdown' and now >= s.fetch('t_go', now):
        s.store('state', 'running')
        s.store('t_start', s.fetch('t_go', now))
        if k == 'record':
            _record(True)
        st = 'running'
    t_rel = None if st == 'idle' else now - s.fetch('t_go', now)     # seconds since bar 1 (negative = count-in)
    p = E().update(t_rel)
    song = E().describe() if E().active() else ''
    if st == 'countdown':
        left = s.fetch('t_go', now) - now
        big = str(p.beats_left) if p is not None else str(int(math.ceil(left)))
        small = ('REC in' if k == 'record' else 'REHEARSE in') + ('   ' + song if song else '')
    if st == 'running':
        t = now - s.fetch('t_start', now)
        small = ('\u25cf REC  ' if k == 'record' else 'REHEARSE  ') + _clock(t)
        if p is not None and not p.counting_in:
            small += '   %s  |  chorus %d  bar %d  |  %s' % (song, p.chorus, p.bar, p.chord.symbol)
    if st == 'idle':
        small = 'Space: start %s' % s.par.Armed.eval() + ('   |   ' + song if song else '')
        pb = PB().tick()
        if pb:
            small = pb + '   (Space: stop)'
    ov = op.Output
    ov.op('count_text').par.text = big
    ov.op('status_text').par.text = small
    rec = (k == 'record' and st != 'idle')
    ov.op('status_text').par.fontcolorr = 1.0
    ov.op('status_text').par.fontcolorg = 0.35 if rec else 1.0
    ov.op('status_text').par.fontcolorb = 0.35 if rec else 1.0
    lvl = op.Analysis.op('out')['level']
    s.par.Status = '%s | %s | %s | input %3d%% | %s' % (
        st.upper() if st != 'running' else (k.upper()), s.par.Mode.eval(), song or 'no chart',
        int((lvl.eval() if lvl is not None else 0) * 100),
        os.path.basename(s.fetch('lasttake', '')) or 'no takes yet')
