# Build the click (/project1/click): a beat you can see and/or hear that NEVER gets into a take.
# Run by build_live.py (uses its helpers). Driven by song/out: tick (0..1 since the last beat, through the
# count-in), downbeat (beat 1 of the bar), active (counting in or running).
#   visual: click/panel in its own window ("Click" window) + a small dot in the preview (preview only)
#   audio:  a short sine tick to the audio interface's outputs (Config > Audio Device); takes record only the
#           guitar input (sources/audio_out), so the click can't reach them
P = op('/project1')
SH = op('/project1/show')
if not has(SH, 'Click'):
    pg = page(SH, 'Click')
    pg.appendMenu('Click', label='Click')
    SH.par.Click.menuNames = ['off', 'visual', 'audio', 'both']
    SH.par.Click.menuLabels = ['Off', 'Visual', 'Audio', 'Visual + Audio']
    pg.appendFloat('Clickvolume', label='Click Volume')
    pg.appendStr('Clickoutputs', label='Click Outputs (e.g. 1 2)')
    pg.appendPulse('Openclick', label='Open Click Window')
    SH.par.Click = 'visual'
    SH.par.Clickvolume = 0.5
    SH.par.Clickoutputs = '1 2'

if not has(SH, 'Clickevery'):
    pg = page(SH, 'Click')
    pg.appendMenu('Clickevery', label='Click Every')
    SH.par.Clickevery.menuNames = ['beat', 'bar', 'form']
    SH.par.Clickevery.menuLabels = ['Beat', 'Bar', 'Form (section tops + count into each section)']
    SH.par.Clickevery = 'beat'

K = ensure(P, baseCOMP, 'click', 1000, 200)
K.par.opshortcut = 'Click'
ON_V = "op.Show.par.Click.eval() in ('visual', 'both')"
ON_A = "op.Show.par.Click.eval() in ('audio', 'both')"
ENV = ("op.Song.op('out')['active'] * op.Song.op('out')['clickon'] * "
       "max(0.0, 1.0 - op.Song.op('out')['tick'] * 4.0)")      # flash decays in 1/4 beat; only on beats that click
ACC = "op.Song.op('out')['accent']"                             # 2 = top of a section, 1 = beat 1, 0 = other beats

# ---- audio tick
osc = ensure(K, audiooscillatorCHOP, 'tick_osc', 0, 0)
osc.par.wavetype = 'sine' if 'sine' in osc.par.wavetype.menuNames else osc.par.wavetype.eval()
osc.par.frequency.expr = "[1050, 1600, 2100][int(%s)]" % ACC
osc.par.amp.expr = "(%s) * (%s) * op.Show.par.Clickvolume * (%s) * [0.8, 1.0, 1.25][int(%s)]" % (ON_A, ENV, ENV, ACC)
left = ensure(K, renameCHOP, 'left', 150, 50)             # same tick on two outputs
left.inputConnectors[0].connect(osc)
left.par.renamefrom, left.par.renameto = '*', 'left'
right = ensure(K, renameCHOP, 'right', 150, -50)
right.inputConnectors[0].connect(osc)
right.par.renamefrom, right.par.renameto = '*', 'right'
dup = ensure(K, mergeCHOP, 'two', 300, 0)
dup.inputConnectors[0].connect(left)
dup.inputConnectors[1].connect(right)
aout = ensure(K, audiodeviceoutCHOP, 'to_interface', 450, 0)
aout.inputConnectors[0].connect(dup)
aout.par.driver = 'asio'
dev = menu_name_for_label(aout.par.device, op.Config.par.Audiodevice.eval())
if dev:
    aout.par.device = dev
REPORT['click_device'] = dev or 'NOT FOUND'
aout.par.active.expr = ON_A
aout.par.active.mode = ParMode.EXPRESSION          # (setting .expr alone left it CONSTANT = off: no audible click)

# ---- visual tick: a square that flashes on every beat (warm on beat 1), beat number, bar and chords
CW, CH = 360, 360
flash = ensure(K, constantTOP, 'flash', 0, -200)
flash.par.resolutionw, flash.par.resolutionh = CW, CH
FL = [(0.55, 0.75, 0.95), (0.95, 0.55, 0.25), (1.0, 0.9, 0.55)]   # other beats: blue, beat 1: warm, section top: gold
for k, ch in enumerate('rgb'):
    getattr(flash.par, 'color' + ch).expr = "[%r, %r, %r][int(%s)] * (0.08 + 0.92 * (%s))" % (
        FL[0][k], FL[1][k], FL[2][k], ACC, ENV)
num = ensure(K, textTOP, 'beat_text', 0, -350)
num.par.outputresolution = 'custom'
num.par.resolutionw, num.par.resolutionh = CW, CH
num.par.bgalpha = 0
num.par.fontsizex = 150
num.par.alignx, num.par.aligny = 'center', 'center'
num.par.text.expr = "op.Song.op('engine').module.click_big()"
info = ensure(K, textTOP, 'info_text', 0, -500)
info.par.outputresolution = 'custom'
info.par.resolutionw, info.par.resolutionh = CW, CH
info.par.bgalpha = 0
info.par.fontsizex = 22
info.par.alignx, info.par.aligny = 'center', 'bottom'
info.par.positiony = 18
info.par.text.expr = "op.Song.op('engine').module.click_info()"
comp = ensure(K, compositeTOP, 'view', 200, -350)
comp.inputConnectors[0].connect(info)
comp.inputConnectors[1].connect(num)
comp.inputConnectors[2].connect(flash)
comp.par.operand = 'over'
panel = ensure(K, containerCOMP, 'panel', 400, -350)
panel.par.w, panel.par.h = CW, CH
panel.par.top = comp.path
win = ensure(K, windowCOMP, 'window', 550, -350)
win.par.winop = panel.path
win.par.title = 'TDlive click'
win.par.winw, win.par.winh = CW, CH
win.par.size = 'custom' if 'custom' in win.par.size.menuNames else win.par.size.eval()
win.par.alwaysontop = True

# ---- preview dot (TDlive window only; never recorded)
dot = ensure(op.Output, circleTOP, 'beat_dot', 300, -500)
dot.par.outputresolution = 'custom'
dot.par.resolutionw.expr, dot.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
dot.par.radiusx.expr = dot.par.radiusy.expr = '0.022'
dot.par.centerx, dot.par.centery = 0.45, 0.42
dot.par.bgalpha = 0
dot.par.borderwidth = 0
for k, ch in enumerate('rgb'):
    getattr(dot.par, 'fillcolor' + ch).expr = "[%r, %r, %r][int(%s)]" % (FL[0][k], FL[1][k], FL[2][k], ACC)
dot.par.fillalpha.expr = "(%s) * (0.15 + 0.85 * (%s))" % (ON_V, ENV)
