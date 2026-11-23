# Build the "Notation" mode (visuals/notation): Michael's three-circle notation drawn live.
# Run by build_live.py (needs its helpers: ensure, synced, page, has).
#   prims (Script TOP, modules/notation/prims.py: chart + song clock + pitch follower -> primitives)
#     -> draw (GLSL TOP, modules/notation/draw.frag: soft lines, rings, discs + glow)
#     -> caption (Text TOP over it, optional) -> out1
V = op('/project1/visuals')
N = ensure(V, baseCOMP, 'notation', 0, -600)
if not has(N, 'Brightness'):
    pg = page(N, 'Notation')
    pg.appendFloat('Brightness', label='Brightness')
    pg.appendFloat('Glow', label='Glow')
    pg.appendFloat('Glowreach', label='Glow Reach')
    pg.appendToggle('Allchords', label="Show The Tune's Harmonic Map (all chords, faint)")
    pg.appendToggle('Labels', label='Caption (section, bar, chord)')
    pg.appendFloat('Melodytrail', label='Played Notes Trail (s)')
    pg.appendFloat('Melodyclarity', label='Pitch Confidence Needed (0..1)')
    for k, v in (('Brightness', 1.6), ('Glow', 0.35), ('Glowreach', 0.025), ('Allchords', True), ('Labels', True),
                 ('Melodytrail', 2.5), ('Melodyclarity', 0.8)):
        N.par[k] = v
        N.par[k].default = v

if not has(N, 'Do'):
    pg = page(N, 'Notation')
    pg.appendMenu('Do', label='Inside The Harmony Circles')
    N.par.Do.menuNames = ['fixed', 'movable']
    N.par.Do.menuLabels = ['Fixed do (C at the top)', "Movable do (the chord's root at the top)"]
    pg.appendToggle('Names', label='Note Names On The Circle Of Fifths')
    pg.appendMenu('Phrasing', label='Phrasing (charts with alternative hearings)')
    N.par.Phrasing.menuNames = ['first', 'second', 'alternate']
    N.par.Phrasing.menuLabels = ['First hearing', 'Second hearing', 'Alternate every chorus']
    N.par.Do, N.par.Names, N.par.Phrasing = 'fixed', False, 'first'

cb = synced(N, textDAT, 'prims_callbacks', 'modules/notation/prims.py', -200, -100)
pr = ensure(N, scriptTOP, 'prims', 0, 0)
pr.par.callbacks = cb.path
pr.par.format = 'rgba32float'
fx = synced(N, textDAT, 'draw_frag', 'modules/notation/draw.frag', 150, 150)
dr = ensure(N, glslTOP, 'draw', 200, 0)
dr.inputConnectors[0].connect(pr)
dr.par.pixeldat = fx.path
dr.par.outputresolution = 'custom'
dr.par.resolutionw.expr, dr.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
dr.par.premultrgbbyalpha = False
dr.par.inputfiltertype = 'nearest'
dr.par.vec0name = 'uLook'
dr.par.vec0valuex.expr = 'parent().par.Brightness'
dr.par.vec0valuey.expr = 'parent().par.Glow'
dr.par.vec0valuez.expr = 'parent().par.Glowreach'
dr.par.vec0valuew.expr = '2.0 / min(op.Config.par.Width, op.Config.par.Height)'
cap = ensure(N, textTOP, 'caption', 200, -150)
cap.par.outputresolution = 'custom'
cap.par.resolutionw.expr, cap.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
cap.par.font = 'Segoe UI'
cap.par.fontsizex.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.026'
cap.par.alignx, cap.par.aligny = 'center', 'bottom'
cap.par.positiony.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.03'
cap.par.fontcolorr, cap.par.fontcolorg, cap.par.fontcolorb = 0.72, 0.74, 0.8
cap.par.bgalpha = 0
cap.par.text.expr = "op('prims_callbacks').module.label() if parent().par.Labels else ''"
spec = ensure(N, tableDAT, 'names_spec', 200, -300)     # note names on the ring (Names on)
nm = ensure(N, textTOP, 'names', 200, -450)
nm.par.outputresolution = 'custom'
nm.par.resolutionw.expr, nm.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
nm.par.font = 'Segoe UI'
nm.par.fontsizex.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.03'
nm.par.alignx, nm.par.aligny = 'center', 'center'
nm.par.fontcolorr, nm.par.fontcolorg, nm.par.fontcolorb = 0.95, 0.93, 0.9
nm.par.bgalpha = 0
nm.par.text = ''
nm.par.specdat = spec.path
nx = ensure(N, executeDAT, 'names_tick', 0, -450)
nx.text = ("def onFrameStart(frame):\n"
           "    if parent().par.Names and op.Show.par.Mode == 'notation':\n"
           "        op('prims_callbacks').module.names_table(op('names_spec'))\n"
           "    elif op('names_spec').numRows > 1:\n"
           "        op('names_spec').clear()\n"
           "    return\n")
nx.par.framestart = True
nx.par.active = True
ov = ensure(N, compositeTOP, 'over', 400, 0)
for c_ in list(ov.inputConnectors):
    c_.disconnect()
ov.inputConnectors[0].connect(cap)
ov.inputConnectors[1].connect(nm)
ov.inputConnectors[2].connect(dr)
ov.par.operand = 'over'
o1 = ensure(N, nullTOP, 'out1', 550, 0)
o1.inputConnectors[0].connect(ov)
REPORT['notation'] = N.path
