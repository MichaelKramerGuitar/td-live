# Build (or rebuild) the TDlive M1 skeleton inside /project1.  Idempotent: safe to run again.
#
#   exec(open(project.folder + '/scripts/build_live.py').read(), globals())     # from the bridge / textport
#
# Architecture (same idea as td-experiment):
#   config (op.Config) ........ output size, fps, devices, folders
#   sources (op.Sources) ...... audio_in (Focusrite ASIO) -> guitar (mono) + audio_out (for takes); camera -> cam
#   analysis (op.Analysis) .... THE BUS: analysis/out = level, hit, low, mid, high  (all 0..1)
#   visuals (op.Visuals) ...... one COMP per mode, each reads only op.Analysis.op('out') and op.Sources.op('cam')
#   output (op.Output) ........ modes switch -> final (what is recorded); preview = final + countdown/status
#   show (op.Show) ............ Rehearse / Record / Stop / Mode / Camera in shot, countdown, Space bar, TDlive window
# Logic lives in modules/show/*.py (synced Text DATs): edit those files, TD picks them up.

P = op('/project1')
REPORT = {}


def ensure(parent, optype, name, x=None, y=None):
    o = parent.op(name)
    if o is None:
        o = parent.create(optype, name)
    if x is not None:
        o.nodeX, o.nodeY = x, y
    return o


def synced(parent, optype, name, relpath, x=None, y=None):
    """A DAT whose text lives in a repo file (edit in VS Code, TD re-reads it)."""
    d = ensure(parent, optype, name, x, y)
    d.par.file = relpath
    d.par.syncfile = True
    d.par.loadonstartpulse.pulse() if hasattr(d.par, 'loadonstartpulse') else None
    return d


def page(comp, name):
    for p in comp.customPages:
        if p.name == name:
            return p
    return comp.appendCustomPage(name)


def has(comp, parname):
    return hasattr(comp.par, parname)


def menu_name_for_label(par, label, default=None):
    labels = list(par.menuLabels)
    return par.menuNames[labels.index(label)] if label in labels else default


# ---------------------------------------------------------------- config
C = ensure(P, baseCOMP, 'config', 0, 400)
C.par.opshortcut = 'Config'
pg = page(C, 'Config')
if not has(C, 'Preset'):
    pg.appendMenu('Preset', label='Format')
    C.par.Preset.menuNames = ['landscape_720', 'portrait_9x16']
    C.par.Preset.menuLabels = ['Landscape 1280x720 (YouTube)', 'Portrait 720x1280 (Reels)']
    pg.appendInt('Width', label='Width')
    pg.appendInt('Height', label='Height')
    pg.appendInt('Fps', label='FPS')
    pg.appendStr('Takesfolder', label='Takes Folder')
    pg2 = page(C, 'Devices')
    pg2.appendStr('Audiodevice', label='Audio Device (ASIO)')
    pg2.appendStr('Guitarchans', label='Guitar Inputs (e.g. 1 2)')
    pg2.appendFloat('Inputgain', label='Input Gain')
    pg2.appendStr('Camera', label='Camera Device')
    C.par.Fps = 30                                       # steady 30 on this laptop (60 = jittery ~34-42)
    C.par.Takesfolder = 'Takes'
    C.par.Audiodevice = 'Focusrite USB ASIO'
    C.par.Guitarchans = '1 2'
    C.par.Inputgain = 6.0
    C.par.Camera = 'HD Pro Webcam C920'
if not has(C, 'Findinput'):
    pgd = page(C, 'Devices')
    pgd.appendPulse('Findinput', label='Find Guitar Input (play for 6 s)')
    pgd.appendStr('Inputinfo', label='Input Info')
    page(C, 'Export').appendStr('Ffmpeg', label='ffmpeg.exe (blank = find it)')
cacts = synced(C, parameterexecuteDAT, 'actions', 'modules/config/actions.py', 0, 0)
cacts.par.op = C.path
cacts.par.pars = 'Findinput'
cacts.par.onpulse = True
cacts.par.valuechange = False
if not has(C, 'Tuning'):
    page(C, 'Guitar').appendStr('Tuning', label='Tuning (low to high, or standard / DADGCF / drop_D / DADGAD)')
    C.par.Tuning = 'standard'
C.par.Width.expr = "{'landscape_720': 1280, 'portrait_9x16': 720}[me.par.Preset.eval()]"
C.par.Height.expr = "{'landscape_720': 720, 'portrait_9x16': 1280}[me.par.Preset.eval()]"
if C.par.Fps.eval() == 60:                               # 2026-11-21: 30 is steadier on this laptop
    C.par.Fps = 30
project.cookRate = C.par.Fps.eval()

# ---------------------------------------------------------------- sources
S_ = ensure(P, baseCOMP, 'sources', 200, 400)
S_.par.opshortcut = 'Sources'
ain = ensure(S_, audiodeviceinCHOP, 'audio_in', 0, 0)
ain.par.driver = 'asio'
dev = menu_name_for_label(ain.par.device, C.par.Audiodevice.eval())
if dev:
    ain.par.device = dev
REPORT['audio_device'] = dev or 'NOT FOUND: ' + C.par.Audiodevice.eval()
# All inputs by name (selecting by index picked the wrong input on this setup - Michael's find), then choose the
# guitar input(s) by channel name from Config > Guitar Inputs.
ain.par.inputselect = 'byname'
ain.par.inputnames = '*'
ain.par.inputindices.expr = ''
gsel = ensure(S_, selectCHOP, 'guitar_inputs', 100, 0)
gsel.inputConnectors[0].connect(ain)
gsel.par.channames.expr = "' '.join('chan%s' % i for i in op.Config.par.Guitarchans.eval().split())"
gtr = ensure(S_, mathCHOP, 'guitar', 200, 0)            # the guitar input(s) averaged to one channel
gtr.inputConnectors[0].connect(gsel)
gtr.par.chanop = 'avg' if 'avg' in gtr.par.chanop.menuNames else gtr.par.chanop.menuNames[-1]
gl = ensure(S_, renameCHOP, 'take_l', 350, -100)          # what goes into a take: the guitar, on both sides
gl.inputConnectors[0].connect(gtr)
gl.par.renamefrom, gl.par.renameto = '*', 'left'
gr = ensure(S_, renameCHOP, 'take_r', 350, -200)
gr.inputConnectors[0].connect(gtr)
gr.par.renamefrom, gr.par.renameto = '*', 'right'
gst = ensure(S_, mergeCHOP, 'take_stereo', 500, -150)
gst.inputConnectors[0].connect(gl)
gst.inputConnectors[1].connect(gr)
aout = ensure(S_, nullCHOP, 'audio_out', 650, -150)       # never more than 2 channels (20 broke the recorder)
aout.inputConnectors[0].connect(gst)
scan = ensure(S_, audiodeviceinCHOP, 'scan_in', 0, 200)   # every input, only while Find Guitar Input listens
scan.par.driver = 'asio'
if dev:
    scan.par.device = dev
scan.par.inputselect = 'byname'
scan.par.inputnames = '*'
scan.par.active = False
synced(S_, textDAT, 'findinput', 'modules/sources/findinput.py', 200, 200)

cam_in = S_.op('camera')
if cam_in is None:                                      # never replace a camera that's already working
    cam_in = ensure(S_, videodeviceinTOP, 'camera', 0, -400)
    cam_in.par.library = 'directshow'
    cdev = menu_name_for_label(cam_in.par.device, C.par.Camera.eval()) if C.par.Camera.eval() else None
    if cdev:
        cam_in.par.device = cdev
    # The C920's HD modes (its MJPEG formats) stall at "Initializing..." in TD 2025.32820 here; 640x480 works.
    if 'f640x480p-30.00hz' in cam_in.par.signalformat.menuNames:
        cam_in.par.signalformat = 'f640x480p-30.00hz'
REPORT['camera_choices'] = list(cam_in.par.device.menuLabels)
REPORT['camera'] = [cam_in.width, cam_in.height, cam_in.warnings()]
nocam = ensure(S_, constantTOP, 'no_camera', 0, -550)
nocam.par.colorr, nocam.par.colorg, nocam.par.colorb = 0.0, 0.0, 0.0
nocam.par.resolutionw, nocam.par.resolutionh = 1280, 720
camsw = ensure(S_, switchTOP, 'camera_or_black', 200, -450)
camsw.inputConnectors[0].connect(nocam)
camsw.inputConnectors[1].connect(cam_in)
camsw.par.index.expr = "1 if op.Show.par.Camerainshot and op('camera').width > 32 and not op('camera').errors() else 0"
cam = ensure(S_, fitTOP, 'cam', 400, -450)               # camera fitted to the output format
cam.inputConnectors[0].connect(camsw)
cam.par.outputresolution = 'custom'
cam.par.resolutionw.expr = 'op.Config.par.Width'
cam.par.resolutionh.expr = 'op.Config.par.Height'
cam.par.fit = 'fill'

# ---------------------------------------------------------------- analysis (the bus)
A = ensure(P, baseCOMP, 'analysis', 400, 400)
A.par.opshortcut = 'Analysis'
src = ensure(A, selectCHOP, 'guitar', 0, 0)
src.par.chop = op.Sources.op('guitar').path


def rms_chain(name, x, y, upstream):
    an = ensure(A, analyzeCHOP, name + '_rms', x, y)
    an.inputConnectors[0].connect(upstream)
    an.par.function = 'rmspower'
    g = ensure(A, mathCHOP, name + '_gain', x + 150, y)
    g.inputConnectors[0].connect(an)
    g.par.gain.expr = 'op.Config.par.Inputgain'
    lim = ensure(A, limitCHOP, name + '_lim', x + 300, y)
    lim.inputConnectors[0].connect(g)
    lim.par.type = 'clamp'
    lim.par.min, lim.par.max = 0, 1
    rn = ensure(A, renameCHOP, name, x + 450, y)
    rn.inputConnectors[0].connect(lim)
    rn.par.renamefrom = '*'
    rn.par.renameto = name
    return rn


raw = rms_chain('raw', 150, 0, src)
lvl_lag = ensure(A, lagCHOP, 'level', 800, 0)            # smooth: quick up, slower down
lvl_lag.inputConnectors[0].connect(raw)
lvl_lag.par.lag1, lvl_lag.par.lag2 = 0.02, 0.25
rnl = ensure(A, renameCHOP, 'level_name', 950, 0)
rnl.inputConnectors[0].connect(lvl_lag)
rnl.par.renamefrom, rnl.par.renameto = '*', 'level'

bands = []
for i, (bname, ftype, cutoff) in enumerate((('low', 'lowpass', 250), ('mid', 'bandpass', 1000), ('high', 'highpass', 3000))):
    y = -150 * (i + 1)
    f = ensure(A, audiofilterCHOP, 'filt_' + bname, 150, y)
    f.inputConnectors[0].connect(src)
    f.par.filter = ftype
    f.par.cutofffrequency = cutoff
    r = rms_chain('b_' + bname, 300, y, f)
    lg = ensure(A, lagCHOP, bname + '_lag', 950, y)
    lg.inputConnectors[0].connect(r)
    lg.par.lag1, lg.par.lag2 = 0.03, 0.3
    rn = ensure(A, renameCHOP, bname, 1100, y)
    rn.inputConnectors[0].connect(lg)
    rn.par.renamefrom, rn.par.renameto = '*', bname
    bands.append(rn)

# onset ("hit"): how far the level jumps above its own slow average
slow = ensure(A, lagCHOP, 'slow', 800, 150)
slow.inputConnectors[0].connect(raw)
slow.par.lag1, slow.par.lag2 = 0.35, 0.35
jump = ensure(A, mathCHOP, 'jump', 950, 150)
jump.inputConnectors[0].connect(raw)
jump.inputConnectors[1].connect(slow)
jump.par.chopop = 'sub' if 'sub' in jump.par.chopop.menuNames else jump.par.chopop.menuNames[2]
trig = ensure(A, triggerCHOP, 'hit_trigger', 1100, 150)
trig.inputConnectors[0].connect(jump)
trig.par.threshold = 0.08
trig.par.attack, trig.par.peak, trig.par.decay = 0.0, 1.0, 0.35
trig.par.sustain, trig.par.release = 0.0, 0.0
hit = ensure(A, renameCHOP, 'hit', 1250, 150)
hit.inputConnectors[0].connect(trig)
hit.par.renamefrom, hit.par.renameto = '*', 'hit'

merge = ensure(A, mergeCHOP, 'merge', 1400, 0)
for i, o in enumerate([rnl, hit] + bands):
    merge.inputConnectors[i].connect(o)
bus = ensure(A, nullCHOP, 'out', 1550, 0)
bus.inputConnectors[0].connect(merge)

# ---------------------------------------------------------------- visuals
V = ensure(P, baseCOMP, 'visuals', 600, 400)
V.par.opshortcut = 'Visuals'
W, H = 'op.Config.par.Width', 'op.Config.par.Height'

# Mode 1 - Mirror: just the camera (framing check, or a clean shot)
mir = ensure(V, baseCOMP, 'mirror', 0, 0)
m_sel = ensure(mir, selectTOP, 'cam', 0, 0)
m_sel.par.top = op.Sources.op('cam').path
m_out = ensure(mir, outTOP, 'out1', 200, 0)
m_out.inputConnectors[0].connect(m_sel)

# Mode 2 - Ripples: every attack drops a ring that spreads out; sustained playing keeps a faint glow.
rip = ensure(V, baseCOMP, 'ripples', 0, -200)
r_cam = ensure(rip, selectTOP, 'cam', 0, 200)
r_cam.par.top = op.Sources.op('cam').path
r_mono = ensure(rip, monochromeTOP, 'cam_mono', 150, 200)
r_mono.inputConnectors[0].connect(r_cam)
r_lvl = ensure(rip, levelTOP, 'cam_dim', 300, 200)
r_lvl.inputConnectors[0].connect(r_mono)
r_lvl.par.brightness1.expr = "0.35 + 0.6 * op.Analysis.op('out')['level']"
ring = ensure(rip, circleTOP, 'ring', 0, 0)
ring.par.outputresolution = 'custom'
ring.par.resolutionw.expr, ring.par.resolutionh.expr = W, H
ring.par.radiusx.expr = ring.par.radiusy.expr = '0.035'
ring.par.fillalpha = 0.0
ring.par.borderwidth = 0.005
ring.par.bgalpha = 0.0
ring.par.borderr.expr = "0.75 + 0.25 * op.Analysis.op('out')['low']"
ring.par.borderg.expr = "0.75 + 0.25 * op.Analysis.op('out')['mid']"
ring.par.borderb.expr = "0.8 + 0.2 * op.Analysis.op('out')['high']"
ring.par.borderalpha.expr = "min(1, op.Analysis.op('out')['hit'] + 0.25 * op.Analysis.op('out')['level'])"
fb = ensure(rip, feedbackTOP, 'feedback', 150, -150)
grow = ensure(rip, transformTOP, 'spread', 300, -150)
grow.inputConnectors[0].connect(fb)
grow.par.sx = grow.par.sy = 1.012
grow.par.extend = 'zero'
fade = ensure(rip, levelTOP, 'fade', 450, -150)
fade.inputConnectors[0].connect(grow)
fade.par.opacity = 0.982
acc = ensure(rip, compositeTOP, 'rings', 600, 0)
acc.inputConnectors[0].connect(ring)
acc.inputConnectors[1].connect(fade)
acc.par.operand = 'add'
fb.inputConnectors[0].connect(ring)
fb.par.top = acc.path
mix = ensure(rip, compositeTOP, 'with_camera', 750, 100)
mix.inputConnectors[0].connect(acc)
mix.inputConnectors[1].connect(r_lvl)
mix.par.operand = 'add'
r_out = ensure(rip, outTOP, 'out1', 900, 100)
r_out.inputConnectors[0].connect(mix)

# ---------------------------------------------------------------- song (chart, key, tempo, form clock)
SG = ensure(P, baseCOMP, 'song', 700, 200)
SG.par.opshortcut = 'Song'
if not has(SG, 'Chart'):
    pg = page(SG, 'Song')
    pg.appendMenu('Chart', label='Chart')
    pg.appendMenu('Key', label='Key')
    pg.appendFloat('Tempo', label='Tempo (bpm)')
    pg.appendInt('Countinbars', label='Count-in Bars')
    pg.appendInt('Frets', label='Frets')
    pg.appendPulse('Reloadcharts', label='Reload Charts')
    SG.par.Tempo = 120
    SG.par.Countinbars = 1
    SG.par.Frets = 19
SG.par.Key.menuNames = ['default', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
SG.par.Key.menuLabels = ["Chart's key"] + list(SG.par.Key.menuNames)[1:]
synced(SG, textDAT, 'engine', 'modules/song/engine.py', 0, 0)
synced(SG, textDAT, 'setup', 'modules/song/setup.py', 0, -150)
sp = synced(SG, parameterexecuteDAT, 'params', 'modules/song/params.py', 0, -300)
sp.par.op = SG.path
sp.par.pars = 'Chart Reloadcharts'
sp.par.onpulse = True
sp.par.valuechange = True
for n in ('now', 'tones', 'positions'):
    ensure(SG, tableDAT, n, 250, {'now': 0, 'tones': -150, 'positions': -300}[n])
clk = ensure(SG, constantCHOP, 'clock', 450, 0)
sgo = ensure(SG, nullCHOP, 'out', 600, 0)
sgo.inputConnectors[0].connect(clk)
SG.op('setup').module.refresh_menu()
REPORT['charts'] = list(SG.par.Chart.menuNames)

# ---------------------------------------------------------------- show control
SH = ensure(P, baseCOMP, 'show', 800, 400)
SH.par.opshortcut = 'Show'
if not has(SH, 'Mode'):
    pg = page(SH, 'Show')
    pg.appendPulse('Rehearse', label='Rehearse (countdown, no take)')
    pg.appendPulse('Record', label='Record (countdown, take)')
    pg.appendPulse('Stop', label='Stop')
    pg.appendMenu('Armed', label='Space Starts')
    SH.par.Armed.menuNames = ['rehearse', 'record']
    SH.par.Armed.menuLabels = ['Rehearse', 'Record']
    pg.appendMenu('Mode', label='Mode')
    pg.appendToggle('Camerainshot', label='Me In Shot (camera)')
    pg.appendInt('Countdown', label='Countdown (s)')
    pg.appendPulse('Openwindow', label='Open TDlive Window')
    pg.appendPulse('Closewindow', label='Close TDlive Window')
    pg.appendStr('Status', label='Status')
    SH.par.Countdown = 4
    SH.par.Camerainshot = True
MODES = [('mirror', 'Mirror (camera)'), ('ripples', 'Ripples'), ('landscape', 'Fretboard Landscape')]
SH.par.Mode.menuNames = [m for m, _ in MODES]
SH.par.Mode.menuLabels = [l for _, l in MODES]
SH.par.Mode.readOnly = False

logic = synced(SH, textDAT, 'logic', 'modules/show/logic.py', 0, 0)
synced(SH, textDAT, 'playback', 'modules/show/playback.py', 0, 150)
synced(SH, textDAT, 'export', 'modules/show/export.py', 0, 300)
acts = synced(SH, parameterexecuteDAT, 'actions', 'modules/show/actions.py', 0, -150)
acts.par.op = SH.path
acts.par.pars = '*'
acts.par.onpulse = True
acts.par.valuechange = False
tick = synced(SH, executeDAT, 'tick', 'modules/show/tick.py', 0, -300)
tick.par.framestart = True
tick.par.start = True                                   # onStart: open the TDlive window
kb = ensure(SH, keyboardinCHOP, 'keyboard', 200, -450)
kb.par.keys = 'space esc r h'
keys = synced(SH, chopexecuteDAT, 'keys', 'modules/show/keys.py', 400, -450)
keys.par.chop = kb.path
keys.par.offtoon = True
keys.par.ontooff = keys.par.whileon = keys.par.whileoff = keys.par.valuechange = False

# ---------------------------------------------------------------- mode: fretboard landscape
exec(open(project.folder + '/scripts/build_landscape.py', encoding='utf-8').read(), globals())
REPORT['landscape'] = landscape_report

# ---------------------------------------------------------------- output
O = ensure(P, baseCOMP, 'output', 1000, 400)
O.par.opshortcut = 'Output'
exec(open(project.folder + '/scripts/build_click.py', encoding='utf-8').read(), globals())   # click (never recorded)
sw = ensure(O, switchTOP, 'modes', 0, 0)
for i, (m, _) in enumerate(MODES):
    s = ensure(O, selectTOP, 'mode_' + m, -200, -120 * i)
    s.par.top = op.Visuals.op(m).op('out1').path
    sw.inputConnectors[i].connect(s)
sw.par.index.expr = 'op.Show.par.Mode.menuIndex'
fit = ensure(O, fitTOP, 'fit', 150, 0)
fit.inputConnectors[0].connect(sw)
fit.par.outputresolution = 'custom'
fit.par.resolutionw.expr, fit.par.resolutionh.expr = W, H
final = ensure(O, nullTOP, 'final', 300, 0)              # <- exactly what gets recorded
final.inputConnectors[0].connect(fit)

ct = ensure(O, textTOP, 'count_text', 300, -200)          # preview-only overlays
ct.par.outputresolution = 'custom'
ct.par.resolutionw.expr, ct.par.resolutionh.expr = W, H
ct.par.fontsizex.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.45'
ct.par.alignx, ct.par.aligny = 'center', 'center'
ct.par.bgalpha = 0
st_ = ensure(O, textTOP, 'status_text', 300, -350)
st_.par.outputresolution = 'custom'
st_.par.resolutionw.expr, st_.par.resolutionh.expr = W, H
st_.par.fontsizex.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.045'
st_.par.alignx, st_.par.aligny = 'left', 'top'
st_.par.positionx.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.03'
st_.par.positiony.expr = '-min(op.Config.par.Width, op.Config.par.Height) * 0.03'
st_.par.bgalpha = 0
# playback of takes (preview only; the recorder keeps recording `final`)
pbk = ensure(O, moviefileinTOP, 'playback', 300, 250)
pbk.par.playmode = 'sequential'                           # plays from the cue point while Play is on
pbk.par.index.expr = ''
pbk.par.play.expr = "op.Show.fetch('playback', False)"
if hasattr(pbk.par, 'extendright'):
    pbk.par.extendright = 'hold' if 'hold' in pbk.par.extendright.menuNames else pbk.par.extendright.eval()
pfit = ensure(O, fitTOP, 'playback_fit', 450, 250)
pfit.inputConnectors[0].connect(pbk)
pfit.par.outputresolution = 'custom'
pfit.par.resolutionw.expr, pfit.par.resolutionh.expr = W, H
mon_src = ensure(O, switchTOP, 'monitor_source', 450, 100)
mon_src.inputConnectors[0].connect(final)
mon_src.inputConnectors[1].connect(pfit)
mon_src.par.index.expr = "1 if op.Show.fetch('playback', False) else 0"
if O.op('playback_audio') is not None and O.op('playback_audio').OPType != 'audiomovieCHOP':
    O.op('playback_audio').destroy()
pam = ensure(O, audiomovieCHOP, 'playback_audio', 450, 400)   # the take's sound, following the movie player
pam.par.moviefileintop = pbk.path
pao = ensure(O, audiodeviceoutCHOP, 'playback_out', 600, 400)
pao.inputConnectors[0].connect(pam)
pao.par.driver = 'asio'
_dev = menu_name_for_label(pao.par.device, op.Config.par.Audiodevice.eval())
if _dev:
    pao.par.device = _dev
pao.par.active.expr = "op.Show.fetch('playback', False)"
pao.par.active.mode = ParMode.EXPRESSION                  # (setting .expr alone left it CONSTANT = off: silent playback)

ov = ensure(O, compositeTOP, 'preview', 500, -100)
ov.inputConnectors[0].connect(st_)
ov.inputConnectors[1].connect(ct)
if O.op('beat_dot') is not None:
    ov.inputConnectors[2].connect(O.op('beat_dot'))
    ov.inputConnectors[3].connect(mon_src)
else:
    ov.inputConnectors[2].connect(mon_src)
ov.par.operand = 'over'

rec = ensure(O, moviefileoutTOP, 'recorder', 500, 100)
rec.inputConnectors[0].connect(final)
rec.par.type = 'movie'
rec.par.videocodec = 'hap'                               # GPU-cheap: ~32 fps while recording vs ~15 with MJPEG
rec.par.audiochop = op.Sources.op('audio_out').path
rec.par.record = False
if O.op('take_wav') is not None:
    O.op('take_wav').destroy()

# ---------------------------------------------------------------- the TDlive window (monitor + buttons)
PANEL_W, MON_H, ROW_H = 960, 540, 52
ROWS = [   # (name, relative width) - row 1: performance, row 2: look + playback
    [('btn_rehearse', 3), ('btn_record', 3), ('btn_chart', 4), ('btn_key', 3),
     ('btn_tempo_down', 1), ('btn_tempo', 2), ('btn_tempo_up', 1)],
    [('btn_mode', 4), ('btn_me', 3), ('btn_camera', 2), ('btn_format', 2), ('btn_take', 3), ('btn_play', 2),
     ('btn_delete', 2), ('btn_export', 3)],
]
BAR_H = ROW_H * len(ROWS) + 6
pn = ensure(SH, containerCOMP, 'panel', 200, 0)
pn.par.w, pn.par.h = PANEL_W, MON_H + BAR_H
pn.par.bgcolorr, pn.par.bgcolorg, pn.par.bgcolorb = 0.06, 0.06, 0.07
mon = ensure(pn, containerCOMP, 'monitor', 0, 0)
mon.par.top = op.Output.op('preview').path
mon.par.h = MON_H
mon.par.w.expr = '%d * op.Config.par.Width / op.Config.par.Height' % MON_H
mon.par.x.expr = '(%d - me.par.w) / 2' % PANEL_W
mon.par.y = BAR_H
meter = ensure(pn, containerCOMP, 'meter', 0, -400)        # input level: set Input Gain so playing sits mid-bar
mc = ensure(meter, constantTOP, 'fill', 0, 0)
mc.par.resolutionw, mc.par.resolutionh = 8, 8
mc.par.colorr.expr = "0.9 if op.Analysis.op('out')['level'] > 0.95 else 0.25"
mc.par.colorg.expr = "0.3 if op.Analysis.op('out')['level'] > 0.95 else 0.8"
mc.par.colorb = 0.35
meter.par.top = mc.path
meter.par.x, meter.par.y, meter.par.h = 0, BAR_H - 4, 4
meter.par.w.expr = "max(1, %d * op.Analysis.op('out')['level'])" % PANEL_W
for old_b in [c for c in pn.children if c.name.startswith('btn_')]:   # rebuild buttons each time
    old_b.destroy()
BUTTONS = []
for r, row in enumerate(ROWS):
    total = sum(wt for _, wt in row)
    x = 0
    y = BAR_H - 6 - ROW_H * (r + 1)
    for bn, wt in row:
        bw = int(PANEL_W * wt / total)
        b = ensure(pn, containerCOMP, bn, 120 * len(BUTTONS), -200)
        b.par.x, b.par.y, b.par.w, b.par.h = x + 3, y + 4, bw - 6, ROW_H - 8
        t = ensure(b, textTOP, 'label', 0, 0)
        t.par.outputresolution = 'custom'
        t.par.resolutionw, t.par.resolutionh = bw - 6, ROW_H - 8
        t.par.fontsizex = 14
        t.par.alignx, t.par.aligny = 'center', 'center'
        t.par.bgcolorr, t.par.bgcolorg, t.par.bgcolorb, t.par.bgalpha = 0.16, 0.16, 0.18, 1
        b.par.top = t.path
        BUTTONS.append((bn, bn))
        x += bw
LABELS = {
    'btn_rehearse': "'Stop' if op.Show.op('logic').module.state() != 'idle' and op.Show.op('logic').module.kind() == 'rehearse' else 'Rehearse'",
    'btn_record': "'Stop' if op.Show.op('logic').module.state() != 'idle' and op.Show.op('logic').module.kind() == 'record' else '\u25cf Record'",
    'btn_chart': "op.Song.par.Chart.menuLabels[op.Song.par.Chart.menuIndex]",
    'btn_key': "'Key: ' + (op.Song.op('engine').module.song().key + ' (chart)' if op.Song.par.Key == 'default' and op.Song.op('engine').module.song() else op.Song.par.Key.eval())",
    'btn_tempo_down': "'\u2212'",
    'btn_tempo': "'%d bpm' % round(op.Song.par.Tempo.eval())",
    'btn_tempo_up': "'+'",
    'btn_mode': "'Mode: ' + op.Show.par.Mode.menuLabels[op.Show.par.Mode.menuIndex]",
    'btn_me': "'Me: ' + (op.Visuals.op('landscape').par.Mestyle.eval().capitalize() if op.Visuals.op('landscape').par.Meplace == 'background' else 'Tile ' + {'top_left': '\\u2196', 'top_right': '\\u2197', 'bottom_left': '\\u2199', 'bottom_right': '\\u2198'}[op.Visuals.op('landscape').par.Meplace.eval()])",
    'btn_camera': "'Cam: ' + ('on' if op.Show.par.Camerainshot else 'off')",
    'btn_format': "'16:9' if op.Config.par.Preset == 'landscape_720' else '9:16'",
    'btn_take': "op.Show.op('playback').module.label()",
    'btn_play': "'\u25a0 Stop' if op.Show.op('playback').module.playing() else '\u25b6 Play'",
    'btn_delete': "'Delete?' if op.Show.op('playback').module.delete_armed() else 'Delete'",
    'btn_export': "op.Show.op('export').module.label()",
}
for bn, ex in LABELS.items():
    pn.op(bn).op('label').par.text.expr = ex
btns = synced(SH, panelexecuteDAT, 'buttons', 'modules/show/buttons.py', 400, 0)
btns.par.panels = ' '.join(pn.op(bn).path for bn, _ in BUTTONS)
btns.par.panelvalue = 'select'
btns.par.offtoon = True
win = ensure(SH, windowCOMP, 'window', 400, -150)
win.par.winop = pn.path
win.par.title = 'TDlive'
win.par.winw, win.par.winh = PANEL_W, MON_H + BAR_H
win.par.size = 'custom' if 'custom' in win.par.size.menuNames else win.par.size.eval()

op('/').time.play = True
SH.op('logic').module.watchdog()                       # keeps the timeline playing from now on
REPORT['errors'] = {o.path: o.errors() for o in P.findChildren(depth=None) if o.errors() and 'mcp_webserver' not in o.path}
REPORT['warnings'] = {o.path: o.warnings() for o in P.findChildren(depth=None) if o.warnings() and 'mcp_webserver' not in o.path}
build_report = REPORT
