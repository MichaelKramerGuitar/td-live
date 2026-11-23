# Export (Text DAT /project1/show/export, synced to this file).
# Takes are Hap .mov: perfect for recording, but most players can't open them. Export turns the selected take
# into an H.264 + AAC .mp4 in Exports/, upscaled to 1080p (1920x1080 landscape, 1080x1920 portrait), playable
# anywhere and ready for YouTube / Instagram. Uses ffmpeg (Config > Ffmpeg, or found automatically), running in
# the background so TouchDesigner keeps going.
import glob
import os
import shutil
import subprocess
import threading
import time

_JOB = {'proc': None, 'out': '', 'done_at': 0, 'error': '', 'dur': 0.0, 'pos': 0.0, 'started': 0.0}


def find_ffmpeg():
    p = op.Config.par.Ffmpeg.eval().strip()
    if p and os.path.exists(p):
        return p
    home = os.path.expanduser('~')
    for c in [shutil.which('ffmpeg')] + \
            glob.glob(home + '/AppData/Local/Microsoft/WinGet/Links/ffmpeg.exe') + \
            glob.glob(home + '/AppData/Local/Microsoft/WinGet/Packages/*FFmpeg*/*/bin/ffmpeg.exe') + \
            glob.glob('C:/ffmpeg*/bin/ffmpeg.exe') + glob.glob('C:/Program Files/ffmpeg*/bin/ffmpeg.exe'):
        if c and os.path.exists(c):
            return c
    return None


def busy():
    return _JOB['proc'] is not None and _JOB['proc'].poll() is None


def export_selected():
    if busy():
        return
    sel = op.Show.op('playback').module.selected()
    if not sel:
        return
    ff = find_ffmpeg()
    if not ff:
        _JOB['error'] = 'need ffmpeg'
        _JOB['done_at'] = time.time()
        return
    src = os.path.join(project.folder, sel)
    folder = os.path.join(project.folder, 'Exports')
    os.makedirs(folder, exist_ok=True)
    portrait = 'portrait' in os.path.basename(sel)
    w, h = (1080, 1920) if portrait else (1920, 1080)
    out = os.path.join(folder, os.path.basename(sel)[:-4] + '_%dx%d.mp4' % (w, h))
    cmd = [ff, '-y', '-loglevel', 'error', '-nostats', '-progress', 'pipe:1', '-i', src,
           '-vf', 'scale=%d:%d:flags=lanczos,format=yuv420p' % (w, h),
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-profile:v', 'high',
           '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out]
    flags = 0x08000000 if os.name == 'nt' else 0     # CREATE_NO_WINDOW: no console popping up
    proc = subprocess.Popen(cmd, creationflags=flags, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, text=True, bufsize=1)
    _JOB.update(proc=proc, out=out, error='', done_at=0, dur=_duration(ff, src), pos=0.0, started=time.time())
    threading.Thread(target=_watch, args=(proc,), daemon=True).start()


def _duration(ff, src):
    # Length of the take in seconds, via ffprobe (installed next to ffmpeg).
    probe = os.path.join(os.path.dirname(ff), 'ffprobe' + ('.exe' if ff.lower().endswith('.exe') else ''))
    if not os.path.exists(probe):
        probe = shutil.which('ffprobe') or probe
    try:
        r = subprocess.run([probe, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src],
                           capture_output=True, text=True, timeout=10,
                           creationflags=0x08000000 if os.name == 'nt' else 0)
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _watch(proc):
    # Background thread: ffmpeg's -progress lines ("out_time_us=12345678") -> _JOB['pos'] in seconds.
    for line in proc.stdout:
        k, _, v = line.strip().partition('=')
        if k in ('out_time_us', 'out_time_ms'):          # both are microseconds (ffmpeg quirk)
            try:
                _JOB['pos'] = max(0.0, int(v) / 1e6)
            except ValueError:
                pass


def progress():
    # 0..1 while exporting, -1 when idle.
    if not busy():
        return -1.0
    if _JOB['dur'] <= 0:
        return 0.0
    return min(1.0, _JOB['pos'] / _JOB['dur'])


def eta():
    f = progress()
    if f <= 0.02:
        return ''
    left = (time.time() - _JOB['started']) * (1 - f) / f
    return '%d:%02d' % (left // 60, left % 60)


def status():
    # Long form for the progress bar under the buttons.
    f = progress()
    if f < 0:
        return ''
    e = eta()
    return 'Exporting %s  %d%%%s' % (os.path.basename(_JOB['out']), round(f * 100), ('  ~' + e + ' left') if e else '')


def label():
    if busy():
        f = progress()
        return 'Export %d%%' % round(f * 100) if _JOB['dur'] > 0 else 'Exporting...'
    p = _JOB['proc']
    if p is not None and _JOB['done_at'] == 0:
        _JOB['done_at'] = time.time()
        if p.returncode != 0:
            _JOB['error'] = 'export failed'
    if time.time() - _JOB['done_at'] < 6:
        if _JOB['error']:
            return 'Export: ' + _JOB['error']
        if p is not None:
            return 'Exported \u2713'
    return 'Export'
