# Export (Text DAT /project1/show/export, synced to this file).
# Takes are Hap .mov: perfect for recording, but most players can't open them. Export turns the selected take
# into an H.264 + AAC .mp4 in Exports/, upscaled to 1080p (1920x1080 landscape, 1080x1920 portrait), playable
# anywhere and ready for YouTube / Instagram. Uses ffmpeg (Config > Ffmpeg, or found automatically), running in
# the background so TouchDesigner keeps going.
import glob
import os
import shutil
import subprocess
import time

_JOB = {'proc': None, 'out': '', 'done_at': 0, 'error': ''}


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
    cmd = [ff, '-y', '-loglevel', 'error', '-i', src,
           '-vf', 'scale=%d:%d:flags=lanczos,format=yuv420p' % (w, h),
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-profile:v', 'high',
           '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', out]
    flags = 0x08000000 if os.name == 'nt' else 0     # CREATE_NO_WINDOW: no console popping up
    _JOB.update(proc=subprocess.Popen(cmd, creationflags=flags), out=out, error='', done_at=0)


def label():
    if busy():
        return 'Exporting...'
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
