# Playback of takes in the TDlive window (Text DAT /project1/show/playback, synced to this file).
# The preview switches from the live picture to the take; its sound goes to the audio interface.
# Recording is untouched: the recorder always records output/final (the live picture), never playback.
import glob
import os
import time


def S():
    return op.Show


def takes():
    """Take files, newest first (relative to the project folder), minus takes waiting to be deleted."""
    folder = os.path.join(project.folder, op.Config.par.Takesfolder.eval())
    files = sorted(glob.glob(os.path.join(folder, '*.mov')), key=os.path.getmtime, reverse=True)
    gone = set(trash())
    return [r for r in (os.path.relpath(f, project.folder).replace('\\', '/') for f in files) if r not in gone]


# ---- deleting: Windows refuses to delete a movie TD still has open (TD can hold it for a while after playback),
# so a confirmed delete hides the take at once and the file is removed as soon as Windows allows (retried every
# couple of seconds, and at the next start). The list survives restarts in Takes/_delete_pending.txt.
def _trash_file():
    return os.path.join(project.folder, op.Config.par.Takesfolder.eval(), '_delete_pending.txt')


def trash():
    try:
        with open(_trash_file(), encoding='utf-8') as f:
            return [l.strip() for l in f if l.strip()]
    except OSError:
        return []


def _save_trash(items):
    path = _trash_file()
    if items:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(items) + '\n')
    elif os.path.exists(path):
        os.remove(path)


def retry_deletes():
    """Try to remove every pending take; keep the ones Windows still refuses."""
    left = []
    for rel in trash():
        ok = True
        for f in (rel, rel[:-4] + '.wav'):
            path = os.path.join(project.folder, f)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                ok = False
        if not ok:
            left.append(rel)
    if left != trash():
        _save_trash(left)
    return left


def selected():
    t = takes()
    sel = S().fetch('take_selected', None)
    if sel in t:
        return sel
    return t[0] if t else None


def select_next():
    t = takes()
    if not t:
        return
    sel = selected()
    i = (t.index(sel) + 1) % len(t) if sel in t else 0
    S().store('take_selected', t[i])


def select_newest():
    t = takes()
    S().store('take_selected', t[0] if t else None)


def label():
    sel = selected()
    if not sel:
        return 'Take: none'
    name = os.path.basename(sel)[:-4]            # 20261121_153012_landscape_landscape_720
    parts = name.split('_')
    hhmm = parts[1][:2] + ':' + parts[1][2:4] if len(parts) > 1 and len(parts[1]) >= 4 else name
    return 'Take %s' % hhmm


def playing():
    return S().fetch('playback', False)


def play():
    sel = selected()
    if not sel or op.Show.op('logic').module.state() != 'idle':
        return
    mf = op.Output.op('playback')
    if mf.par.file.eval() != sel:
        mf.par.file = sel
    mf.par.cuepulse.pulse()                    # from the start; sound follows the movie (playback_audio)
    S().store('playback', True)
    S().store('t_play', absTime.seconds)


def stop():
    S().store('playback', False)


def delete_armed():
    return time.time() - S().fetch('delete_armed_at', -100) < 4.0     # real clock: 4 s to confirm


def delete_selected():
    """First click arms (label 'Delete?'), a second click within 4 s deletes the selected take (.mov, and a .wav of the same name if there is one)."""
    sel = selected()
    if not sel:
        return
    if not delete_armed():
        S().store('delete_armed_at', time.time())
        return
    S().store('delete_armed_at', -100)
    stop()
    mf = op.Output.op('playback')
    if mf.par.file.eval() == sel:
        mf.par.file = app.samplesFolder + '/Map/Banana.tif'   # let go of the movie as far as TD can
    if op.Output.op('recorder').par.file.eval() == sel:
        op.Output.op('recorder').par.file = ''
    _save_trash(trash() + [sel])
    S().store('take_selected', None)
    op.Show.op('logic').module.later(retry_deletes, 30)


def toggle():
    stop() if playing() else play()


def tick():
    """Called every frame by show/logic: advance the playback index, stop at the end. Returns status text."""
    if absTime.frame % 60 == 0 and trash():
        retry_deletes()
    if not playing():
        return None
    mf = op.Output.op('playback')
    t = absTime.seconds - S().fetch('t_play', absTime.seconds)
    fps = op.Config.par.Fps.eval()
    n = max(1, mf.numImages)
    if t * fps >= n:
        stop()
        return None
    total = n / float(fps)
    return '▶ PLAYBACK  %s   %d:%02d / %d:%02d' % (label()[5:], int(t // 60), int(t % 60), int(total // 60), int(total % 60))
