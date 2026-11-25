# Build the "Harmony Galaxy" mode (visuals/galaxy): the first Harmony Journey picture.
# Run by build_live.py (needs its helpers: ensure, synced, page, has).
#   prims (Script TOP, modules/galaxy/world.py: chart + Michael's analysis + song clock -> projected primitives)
#     -> grid (GLSL TOP, layer 1, half resolution)  \
#     -> bodies (GLSL TOP, layer 0, full resolution) -> add -> + key names + caption -> out1
V = op('/project1/visuals')
G = ensure(V, baseCOMP, 'galaxy', 0, -800)
if not has(G, 'View'):
    pg = page(G, 'Galaxy')
    pg.appendMenu('View', label='Camera')
    G.par.View.menuNames = ['follow', 'overview']
    G.par.View.menuLabels = ['Follow the traveller', 'From above']
    pg.appendFloat('Tilt', label='Camera Tilt (degrees above the plane)')
    pg.appendFloat('Spin', label='Camera Spin (degrees)')
    pg.appendToggle('Drift', label='Slow Drift Around')
    pg.appendToggle('Grid', label='Gravity Grid')
    pg.appendToggle('Tether', label='Tether Home')
    pg.appendToggle('Names', label='Key Names')
    pg.appendToggle('Labels', label='Caption')
    pg.appendFloat('Trail', label='Traveller Trail (s)')
    pg.appendFloat('Brightness', label='Brightness')
    pg.appendFloat('Glow', label='Glow')
    pg.appendFloat('Glowreach', label='Glow Reach')
    for k, v in (('View', 'follow'), ('Tilt', 38.0), ('Spin', 0.0), ('Drift', True), ('Grid', True),
                 ('Tether', True), ('Names', True), ('Labels', True), ('Trail', 2.5), ('Brightness', 1.5),
                 ('Glow', 0.35), ('Glowreach', 0.02)):
        G.par[k] = v
        G.par[k].default = v

cb = synced(G, textDAT, 'world_callbacks', 'modules/galaxy/world.py', -200, -100)
pr = ensure(G, scriptTOP, 'prims', 0, 0)
pr.par.callbacks = cb.path
pr.par.format = 'rgba32float'
fx = synced(G, textDAT, 'draw_frag', 'modules/notation/draw.frag', 150, 150)   # the same drawing shader
passes = {}
for name, layer, scale, y in (('grid', 1, 0.5, 100), ('bodies', 0, 1.0, -50)):
    d = ensure(G, glslTOP, name, 200, y)
    d.inputConnectors[0].connect(pr)
    d.par.pixeldat = fx.path
    d.par.outputresolution = 'custom'
    d.par.resolutionw.expr = 'int(op.Config.par.Width * %s)' % scale
    d.par.resolutionh.expr = 'int(op.Config.par.Height * %s)' % scale
    d.par.premultrgbbyalpha = False
    d.par.inputfiltertype = 'nearest'
    d.par.vec0name = 'uLook'
    d.par.vec0valuex.expr = 'parent().par.Brightness'
    d.par.vec0valuey.expr = 'parent().par.Glow'
    d.par.vec0valuez.expr = 'parent().par.Glowreach'
    d.par.vec0valuew.expr = '2.0 / (min(op.Config.par.Width, op.Config.par.Height) * %s)' % scale
    d.par.vec1name = 'uLayer'
    d.par.vec1valuex = layer
    passes[name] = d
add = ensure(G, compositeTOP, 'add', 400, 50)
for c_ in list(add.inputConnectors):
    c_.disconnect()
add.inputConnectors[0].connect(passes['bodies'])
add.inputConnectors[1].connect(passes['grid'])
add.par.operand = 'add'
add.par.outputresolution = 'custom'
add.par.resolutionw.expr, add.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'

spec = ensure(G, tableDAT, 'names_spec', 200, -300)
nm = ensure(G, textTOP, 'names', 400, -300)
nm.par.outputresolution = 'custom'
nm.par.resolutionw.expr, nm.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
nm.par.font = 'Segoe UI'
nm.par.fontsizex.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.026'
nm.par.fontcolorr, nm.par.fontcolorg, nm.par.fontcolorb = 0.92, 0.9, 0.86
nm.par.bgalpha = 0
nm.par.text.expr = "'' if op('names_spec').numRows >= 0 else ''"
nm.par.fontalpha.expr = '0.85 if parent().par.Names else 0.0'
nm.par.specdat = spec.path
nx = ensure(G, executeDAT, 'names_tick', 0, -300)
nx.text = ("# fills names_spec and re-cooks the names Text TOP (it doesn't notice spec table changes by itself)\n"
           "def onFrameStart(frame):\n"
           "    if op.Show.par.Mode == 'galaxy':\n"
           "        op('world_callbacks').module.names_table(op('names_spec'))\n"
           "        op('names').cook(force=True)\n"
           "    return\n")
nx.par.framestart = True
nx.par.active = True
cap = ensure(G, textTOP, 'caption', 400, -450)
cap.par.outputresolution = 'custom'
cap.par.resolutionw.expr, cap.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
cap.par.font = 'Segoe UI'
cap.par.fontsizex.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.026'
cap.par.alignx, cap.par.aligny = 'center', 'bottom'
cap.par.positiony.expr = 'min(op.Config.par.Width, op.Config.par.Height) * 0.03'
cap.par.fontcolorr, cap.par.fontcolorg, cap.par.fontcolorb = 0.72, 0.74, 0.8
cap.par.bgalpha = 0
cap.par.text.expr = "op('world_callbacks').module.label() if parent().par.Labels and absTime.frame else ''"   # (absTime: re-evaluate every frame)
ov = ensure(G, compositeTOP, 'over', 600, 0)
for c_ in list(ov.inputConnectors):
    c_.disconnect()
ov.inputConnectors[0].connect(cap)
ov.inputConnectors[1].connect(nm)
ov.inputConnectors[2].connect(add)
ov.par.operand = 'over'
o1 = ensure(G, nullTOP, 'out1', 750, 0)
o1.inputConnectors[0].connect(ov)
REPORT['galaxy'] = G.path
