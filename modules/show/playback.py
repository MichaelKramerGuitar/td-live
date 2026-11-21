# Playback of takes in the TDlive window (Text DAT /project1/show/playback, synced to this file).
# The preview switches from the live picture to the take; its sound goes to the audio interface.
# Recording is untouched: the recorder always records output/final (the live picture), never playback.
import glob
import os


def S():
    return op.Show


def takes():
    """Take files, newest first (relative to the project folder)."""
    folder = os.path.join(project.folder, op.Config.par.Takesfolder.eval())
    files = sorted(glob.glob(os.path.join(folder, '*.mov')), key=os.path.getmtime, reverse=True)
    return [os.path.relpath(f, project.folder).replace('\\', '/') for f in files]


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
    return absTime.seconds - S().fetch('delete_armed_at', -100) < 3.0


def delete_selected():
    """First click arms (label 'Delete?'), a second click within 3 s deletes the selected take (.mov, and a .wav of the same name if there is one)."""
    sel = selected()
    if not sel:
        return
    if not delete_armed():
        S().store('delete_armed_at', absTime.seconds)
        return
    S().store('delete_armed_at', -100)
    stop()                                      # 1) stop playing ...
    S().store('delete_pending', sel)
    run("op.Show.op('playback').module._release()", delayFrames=10)


def _release():
    """2) ... let go of the file a few frames later (never while it is playing) ..."""
    sel = S().fetch('delete_pending', None)
    if op.Output.op('playback').par.file.eval() == sel:
        # Clearing the path isn't enough: the Movie File In keeps the last movie open until it opens another
        # file. Point it at TD's built-in sample image so Windows lets go of the take.
        op.Output.op('playback').par.file = app.samplesFolder + '/Map/Banana.tif'
    if op.Output.op('recorder').par.file.eval() == sel:
        op.Output.op('recorder').par.file = ''
    run("op.Show.op('playback').module._finish_delete()", delayFrames=20)


def _finish_delete():
    """3) ... and delete it."""
    sel = S().fetch('delete_pending', None)
    if not sel:
        return
    S().store('delete_pending', None)
    for f in (sel, sel[:-4] + '.wav'):
        path = os.path.join(project.folder, f)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            debug('could not delete %s: %s' % (f, e))
    S().store('take_selected', None)


def toggle():
    stop() if playing() else play()


def tick():
    """Called every frame by show/logic: advance the playback index, stop at the end. Returns status text."""
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
