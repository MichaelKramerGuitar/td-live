# Song engine (Text DAT /project1/song/engine, synced to this file).
# Bridges the repo's pure-Python harmony tools (tools/harmony.py, formclock.py, chartlib.py) into TD:
#   - loads the chart picked in op.Song (Chart / Key / Tempo), cached until something changes
#   - every frame: where are we (chorus, section, bar, beat, chord) -> song/now (table) + song/clock (CHOP)
#   - on every chord change: the chord-scale (song/tones) and its fretboard positions (song/positions),
#     with weights and palette colours, for the visuals (the fretboard landscape reads these)
import glob
import math
import os
import sys

TOOLS = os.path.join(project.folder, 'tools')
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import chartlib as cl   # noqa: E402
import formclock as fc  # noqa: E402
import harmony as h     # noqa: E402

_CACHE = {'sig': None, 'song': None, 'chord_index': None, 'palette': None, 'error': ''}


def chart_files():
    return sorted(glob.glob(os.path.join(project.folder, 'charts', '*.yaml')))


def chart_menu():
    """[(id, title)] for charts that can be clocked (have changes)."""
    out = []
    for p in chart_files():
        try:
            c = cl.load_chart(p)
            if c.get('changes'):
                out.append((c['id'], c['title']))
        except Exception:
            pass
    return out


def palette():
    if _CACHE['palette'] is None:
        _CACHE['palette'] = cl.load_palette(os.path.join(project.folder, 'synesthesia', 'palette.yaml'))
    return _CACHE['palette']


def active():
    return op.Song.par.Chart.eval() not in ('', 'none')


def song():
    """The current Song (re-built when chart / key / tempo / chart file change), or None."""
    S = op.Song
    if not active():
        return None
    cid = S.par.Chart.eval()
    path = os.path.join(project.folder, 'charts', cid + '.yaml')
    key = S.par.Key.eval()
    sig = (cid, key, S.par.Tempo.eval(), os.path.getmtime(path) if os.path.exists(path) else 0)
    if sig != _CACHE['sig']:
        _CACHE['sig'] = sig
        try:
            chart = cl.load_chart(path)
            _CACHE['song'] = fc.Song(chart, key=None if key == 'default' else key, bpm=S.par.Tempo.eval())
            _CACHE['error'] = ''
        except Exception as e:
            _CACHE['song'] = None
            _CACHE['error'] = str(e)
        _CACHE['chord_index'] = None
    return _CACHE['song']


def describe():
    s = song()
    if s is None:
        return _CACHE['error'] or 'no chart'
    return '%s in %s, %d bpm' % (s.chart['title'], s.key, round(s.bpm))


def count_in_seconds():
    s = song()
    return s.count_in_seconds(op.Song.par.Countinbars.eval()) if s else None


def update(seconds):
    """Called every frame by show/logic with time since bar 1 (negative while counting in), or None when idle."""
    S = op.Song
    s = song()
    now, clock = S.op('now'), S.op('clock')
    if s is None or seconds is None:
        vals = {'playing': 0, 'counting_in': 0, 'beat_phase': 0, 'bar_phase': 0, 'beat': 0, 'bar': 0,
                'chorus': 0, 'chord_index': -1, 'tick': 1, 'downbeat': 0, 'active': 0, 'beats_left': 0}
        _set_clock(clock, vals)
        _set_now(now, {'chart': describe(), 'state': 'idle'})
        if s is not None and _CACHE['chord_index'] != 'idle':      # show the first chord while idle
            _CACHE['chord_index'] = 'idle'
            _write_chord(s.events[0][2])
        return None
    p = s.at(seconds)
    # Click timing, continuous through the count-in: tick = 0..1 since the last beat; downbeat = beat 1 of a bar.
    beats = seconds / s.sec_per_beat
    tick = beats - math.floor(beats)
    downbeat = 1 if int(math.floor(beats)) % s.beats_per_bar == 0 else 0
    _set_clock(clock, {'playing': 0 if p.counting_in else 1, 'counting_in': 1 if p.counting_in else 0,
                       'beat_phase': p.beat_phase, 'bar_phase': p.bar_phase, 'beat': p.beat, 'bar': p.bar,
                       'chorus': p.chorus, 'chord_index': p.chord_index,
                       'tick': tick, 'downbeat': downbeat, 'active': 1, 'beats_left': p.beats_left})
    ch = p.chord or p.next_chord
    _set_now(now, {'chart': describe(), 'state': 'count-in' if p.counting_in else 'playing',
                   'chorus': p.chorus, 'section': p.section, 'pass': p.pass_, 'bar': p.bar,
                   'bar_in_section': p.bar_in_section, 'beat': p.beat, 'beats_left': p.beats_left,
                   'chord': ch.symbol, 'numeral': ch.numeral, 'root': ch.root, 'quality': ch.quality,
                   'scale': ch.scale, 'next': p.next_chord.symbol})
    if p.chord_index != _CACHE['chord_index']:
        _CACHE['chord_index'] = p.chord_index
        _write_chord(ch)
    return p


def _set_clock(chop, vals):
    for i, (k, v) in enumerate(vals.items()):
        chop.par['name%d' % i] = k
        chop.par['value%d' % i] = v


def _set_now(dat, d):
    dat.clear()
    for k, v in d.items():
        dat.appendRow([k, v])


def _write_chord(ch):
    pal = palette()
    tones = op.Song.op('tones')
    tones.clear()
    tones.appendRow(['note', 'interval', 'role', 'weight', 'r', 'g', 'b'])
    for n, iv, role, w in ch.scale_tones():
        r, g, b = cl.hex_to_rgb(cl.color_for(n, pal))
        tones.appendRow([n, iv, role, w, r, g, b])
    pos = op.Song.op('positions')
    pos.clear()
    pos.appendRow(['string', 'fret', 'note', 'role', 'weight', 'r', 'g', 'b'])
    for s, f, n, iv, role, w in h.fretboard(ch, op.Config.par.Tuning.eval(), op.Song.par.Frets.eval()):
        r, g, b = cl.hex_to_rgb(cl.color_for(n, pal))
        pos.appendRow([s, f, n, role, w, r, g, b])
