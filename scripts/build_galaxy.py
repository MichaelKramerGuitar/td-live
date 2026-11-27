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

G.par.View.menuNames = ['bodycam', 'follow', 'overview']
G.par.View.menuLabels = ['Body cam (riding with the traveller)', 'Follow the traveller', 'From above']
if not has(G, 'Bodycamfov'):
    page(G, 'Galaxy').appendFloat('Bodycamfov', label='Body Cam Field Of View (degrees)')
    G.par.Bodycamfov = 62.0
    G.par.Bodycamfov.default = 62.0
    G.par.View = 'bodycam'

if not has(G, 'Protagonist'):
    pg = page(G, 'Galaxy')
    pg.appendMenu('Protagonist', label='Protagonist')
    pg.appendFloat('Whispclarity', label='Whisp: Pitch Confidence Needed (0..1)')
    pg.appendFloat('Gridres', label='Gravity Grid Resolution (fraction of the frame)')
    G.par.Whispclarity, G.par.Gridres = 0.8, 0.25
    G.par.Whispclarity.default, G.par.Gridres.default = 0.8, 0.25
G.par.Protagonist.menuNames = ['comet', 'whisp']
G.par.Protagonist.menuLabels = ['Comet', 'Melody whisp (your line, from the pitch follower)']

cb = synced(G, textDAT, 'world_callbacks', 'modules/galaxy/world.py', -200, -100)
pr = ensure(G, scriptTOP, 'prims', 0, 0)
pr.par.callbacks = cb.path
pr.par.format = 'rgba32float'
fx = synced(G, textDAT, 'draw_frag', 'modules/notation/draw.frag', 150, 150)   # the same drawing shader
passes = {}
for name, layer, scale, y in (('grid', 1, 'parent().par.Gridres', 100), ('bodies', 0, '1.0', -50)):
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
    d.par.vec0valuey.expr = 'parent().par.Glow * (0.6 if %d else 1.0)' % layer
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

# ---------------------------------------------------------------- the Attractor texture (GPU particles)
# att_seeds (Script TOP: points on each attractor) + att_fb (last frame) -> att_sim (GLSL: the simulation, one pixel
# per particle) -> att_col (colours) -> att_geo (instanced billboards) -> att_render (camera att_cam, set each frame to
# match the galaxy's own camera) -> points / trails / both -> + the stars and planets (or alone) -> texture switch.
if not has(G, 'Texture'):
    pg = page(G, 'Attractor')
    pg.appendMenu('Texture', label='Texture')
    pg.appendMenu('Attractorview', label='Attractor View')
    pg.appendMenu('Particlestyle', label='Particles As')
    pg.appendInt('Particles', label='Particles (thousands)')
    pg.appendFloat('Attractorsize', label='Attractor Size (world)')
    pg.appendFloat('Homeshare', label='Share Of Particles That Stay Home')
    pg.appendFloat('Particlebright', label='Particle Brightness')
    pg.appendFloat('Particlesize', label='Particle Size')
    pg.appendFloat('Trailfade', label='Trail Length (fade per frame)')
    pg.appendFloat('Simspeed', label='Flow Speed')
    for k, v in (('Particles', 32), ('Attractorsize', 0.16), ('Homeshare', 0.25), ('Particlebright', 0.15),
                 ('Particlesize', 0.004), ('Trailfade', 0.9), ('Simspeed', 1.6)):
        G.par[k] = v
        G.par[k].default = v
G.par.Texture.menuNames = ['lines', 'attractor']
G.par.Texture.menuLabels = ['Lines (live-03)', 'Attractor']
G.par.Attractorview.menuNames = ['stars', 'abstract']
G.par.Attractorview.menuLabels = ['With the stars and planets', 'Abstract (particles only)']
G.par.Particlestyle.menuNames = ['points', 'trails', 'both']
G.par.Particlestyle.menuLabels = ['Points', 'Trails', 'Both']

seedcb = synced(G, textDAT, 'att_seeds_callbacks', 'modules/galaxy/seeds.py', 900, 400)
seeds = ensure(G, scriptTOP, 'att_seeds', 1050, 400)
seeds.par.callbacks = seedcb.path
seeds.par.format = 'rgba32float'
ini = ensure(G, constantTOP, 'att_init', 900, 250)
ini.par.format = 'rgba32float'
ini.par.outputresolution = 'custom'
ini.par.resolutionw = 256
ini.par.resolutionh.expr = 'max(1, int(parent().par.Particles * 1000 / 256))'
ini.par.colorr = ini.par.colorg = ini.par.colorb = 0.0
ini.par.alpha = -1.0
fb = ensure(G, feedbackTOP, 'att_fb', 1050, 250)
fb.inputConnectors[0].connect(ini)
simdat = synced(G, textDAT, 'att_sim_frag', 'modules/galaxy/attractor_sim.frag', 1050, 550)
sim = ensure(G, glslTOP, 'att_sim', 1200, 300)
for c_ in list(sim.inputConnectors):
    c_.disconnect()
sim.inputConnectors[0].connect(fb)
sim.inputConnectors[1].connect(seeds)
sim.par.pixeldat = simdat.path
sim.par.format = 'rgba32float'
sim.par.inputfiltertype = 'nearest'
sim.par.outputresolution = 'useinput'
sim.seq.vec.numBlocks = max(4, sim.seq.vec.numBlocks)
for i, uname in enumerate(('uHome', 'uLocal', 'uSim', 'uStep')):
    getattr(sim.par, 'vec%dname' % i).val = uname
sim.par.vec3valuey = 3
sim.par.vec3valuez.expr = 'parent().par.Simspeed'
fb.par.top = sim.path
coldat = synced(G, textDAT, 'att_col_frag', 'modules/galaxy/attractor_color.frag', 1200, 550)
col = ensure(G, glslTOP, 'att_col', 1350, 300)
col.inputConnectors[0].connect(sim)
col.par.pixeldat = coldat.path
col.par.format = 'rgba16float'
col.par.inputfiltertype = 'nearest'
col.par.outputresolution = 'useinput'
col.seq.vec.numBlocks = max(2, col.seq.vec.numBlocks)
for i, uname in enumerate(('uHomeCol', 'uLocalCol')):
    getattr(col.par, 'vec%dname' % i).val = uname

geo = ensure(G, geometryCOMP, 'att_geo', 1500, 150)
for ch in list(geo.children):
    if ch.name not in ('quad', 'att_mat', 'att_vert', 'att_frag'):
        ch.destroy()
quad = ensure(geo, rectangleSOP, 'quad', 0, 0)
quad.par.sizex = quad.par.sizey = 1.0
quad.render = quad.display = True
geo.par.instancing = True
geo.par.instanceop = sim.path
geo.par.instancetx, geo.par.instancety, geo.par.instancetz = 'r', 'g', 'b'
geo.par.instancecolorop = col.path
geo.par.instancer, geo.par.instanceg, geo.par.instanceb = 'r', 'g', 'b'
vd = synced(G, textDAT, 'att_vert', 'modules/galaxy/particle.vert', 1350, 50)
pd = synced(G, textDAT, 'att_frag', 'modules/galaxy/particle.frag', 1350, -50)
mat = ensure(G, glslMAT, 'att_mat', 1500, 0)
mat.par.vdat, mat.par.pdat = vd.path, pd.path
mat.par.vec0name = 'uPoint'
mat.par.vec0valuex.expr = 'parent().par.Particlesize'
mat.par.blending = True
mat.par.srcblend, mat.par.destblend = 'one', 'one'
mat.par.depthtest = False
mat.par.depthwriting = False
geo.par.material = mat.path
camo = ensure(G, cameraCOMP, 'att_cam', 1500, -150)
vm = list(camo.par.viewanglemethod.menuNames)
camo.par.viewanglemethod.expr = "%r if op.Config.par.Width >= op.Config.par.Height else %r" % (
    [m for m in vm if 'vert' in m.lower()][0], [m for m in vm if 'hor' in m.lower()][0])
camo.par.near = 0.01
rend = ensure(G, renderTOP, 'att_render', 1650, 150)
rend.par.camera = camo.path
rend.par.geometry = geo.path
rend.par.outputresolution = 'custom'
rend.par.resolutionw.expr, rend.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
rend.par.format = 'rgba16float'
rend.par.bgcolora = 0
# trails: last frame faded + this frame
tfb = ensure(G, feedbackTOP, 'att_trail_fb', 1650, 0)
tfb.inputConnectors[0].connect(rend)
fade = ensure(G, levelTOP, 'att_fade', 1800, 0)
fade.inputConnectors[0].connect(tfb)
fade.par.brightness1.expr = 'parent().par.Trailfade'
trail = ensure(G, compositeTOP, 'att_trail', 1950, 50)
for c_ in list(trail.inputConnectors):
    c_.disconnect()
trail.inputConnectors[0].connect(rend)
trail.inputConnectors[1].connect(fade)
trail.par.operand = 'add'
trail.par.format = 'rgba16float'
tfb.par.top = trail.path
both = ensure(G, compositeTOP, 'att_both', 2100, 100)
for c_ in list(both.inputConnectors):
    c_.disconnect()
both.inputConnectors[0].connect(rend)
both.inputConnectors[1].connect(trail)
both.par.operand = 'add'
sty = ensure(G, switchTOP, 'att_style', 2250, 150)
for c_ in list(sty.inputConnectors):
    c_.disconnect()
for i, t_ in enumerate((rend, trail, both)):
    sty.inputConnectors[i].connect(t_)
sty.par.index.expr = "['points', 'trails', 'both'].index(parent().par.Particlestyle.eval())"
tone_ = ensure(G, glslTOP, 'att_tone', 2400, 150)            # soft tone map: dense regions glow instead of clipping
tone_.inputConnectors[0].connect(sty)
tdat = ensure(G, textDAT, 'att_tone_frag', 2400, 0)
tdat.text = ("out vec4 fragColor;\nvoid main() {\n    vec4 c = texture(sTD2DInputs[0], vUV.st);\n"
             "    fragColor = TDOutputSwizzle(vec4(1.0 - exp(-c.rgb), 1.0));\n}\n")
tone_.par.pixeldat = tdat.path
withb = ensure(G, compositeTOP, 'att_withbodies', 2550, 150)
for c_ in list(withb.inputConnectors):
    c_.disconnect()
withb.inputConnectors[0].connect(tone_)
withb.inputConnectors[1].connect(passes['bodies'])
withb.par.operand = 'add'
asel = ensure(G, switchTOP, 'att_view', 2700, 150)
for c_ in list(asel.inputConnectors):
    c_.disconnect()
asel.inputConnectors[0].connect(withb)
asel.inputConnectors[1].connect(tone_)
asel.par.index.expr = "0 if parent().par.Attractorview == 'stars' else 1"
tsel = ensure(G, switchTOP, 'texture', 2850, 50)
for c_ in list(tsel.inputConnectors):
    c_.disconnect()
tsel.inputConnectors[0].connect(add)
tsel.inputConnectors[1].connect(asel)
tsel.par.index.expr = "0 if parent().par.Texture == 'lines' else 1"
for c_ in list(ov.inputConnectors):
    c_.disconnect()
ov.inputConnectors[0].connect(cap)
ov.inputConnectors[1].connect(nm)
ov.inputConnectors[2].connect(tsel)
# the per-frame link (camera + simulation inputs) rides on names_tick
nx.text = ("# fills names_spec (re-cooking the names Text TOP), points the particle camera, feeds the simulation\n"
           "def onFrameStart(frame):\n"
           "    if op.Show.par.Mode == 'galaxy':\n"
           "        m = op('world_callbacks').module\n"
           "        m.names_table(op('names_spec'))\n"
           "        op('names').cook(force=True)\n"
           "        m.frame_update(parent())\n"
           "    return\n")

# ---------------------------------------------------------------- the Fluid texture (ink in water, top-down)
# A GPU fluid on the galaxy plane (stable fluids: advect -> forces -> pressure solve -> project), its ink, and the
# bat's pings (a wave equation whose speed follows the depth of the harmony's creek bed). Python feeds the
# traveller, its notes, the current and the bed each frame (world.fluid_update, fluid_tops.py).
if not has(G, 'Fluidres'):
    pg = page(G, 'Fluid')
    pg.appendFloat('Fluidres', label='Simulation Resolution (fraction of the frame)')
    pg.appendFloat('Dyeres', label='Ink Resolution (fraction of the frame)')
    pg.appendFloat('Fluidspan', label='World Span (top to bottom)')
    pg.appendMenu('Current', label='Background Current')
    pg.appendFloat('Currentstrength', label='Current Strength')
    pg.appendFloat('Viscosity', label='Viscosity (damping per frame)')
    pg.appendFloat('Vorticity', label='Swirl (vorticity confinement)')
    pg.appendFloat('Push', label='Traveller Push')
    pg.appendFloat('Dyeamount', label='Ink Amount')
    pg.appendFloat('Dyedecay', label='Ink Persistence (per frame)')
    pg.appendFloat('Inkbright', label='Ink Brightness')
    pg.appendFloat('Bed', label='Creek Bed (harmony landscape) Strength')
    pg.appendFloat('Beddrag', label='Drag Over The Shallows')
    pg.appendMenu('Pings', label='Pings (the bat)')
    pg.appendFloat('Pingsize', label='Ping Strength')
    pg.appendFloat('Wavespeed', label='Ping Speed')
    for k, v in (('Fluidres', 0.2), ('Dyeres', 0.5), ('Fluidspan', 2.4), ('Currentstrength', 0.4),
                 ('Viscosity', 0.004), ('Vorticity', 0.25), ('Push', 1.2), ('Dyeamount', 0.08),
                 ('Dyedecay', 0.992), ('Inkbright', 1.2), ('Bed', 1.0), ('Beddrag', 0.04), ('Pingsize', 0.6),
                 ('Wavespeed', 1.0)):
        G.par[k] = v
        G.par[k].default = v
G.par.Current.menuNames = ['none', 'home', 'form']
G.par.Current.menuLabels = ['None', 'Pull home (whirlpools at home and the local key)', 'The form (a stream turning with the chorus)']
G.par.Pings.menuNames = ['every', 'long', 'off']
G.par.Pings.menuLabels = ['Every note', 'Only long notes', 'Off']
if G.par.Current.eval() not in ('none', 'home', 'form'):
    G.par.Current = 'home'
G.par.Texture.menuNames = ['lines', 'attractor', 'fluid']
G.par.Texture.menuLabels = ['Lines (live-03)', 'Attractor', 'Fluid (ink in water)']

FL = project.folder + '/modules/galaxy/fluid/'
COMMON = open(FL + 'common.glsl', encoding='utf-8').read()
UNIFORMS = ['uTrav', 'uInj', 'uDye', 'uFlow', 'uHome', 'uBed', 'uMisc']
SIM_RES = ('int(op.Config.par.Width * parent().par.Fluidres)', 'int(op.Config.par.Height * parent().par.Fluidres)')
DYE_RES = ('int(op.Config.par.Width * parent().par.Dyeres)', 'int(op.Config.par.Height * parent().par.Dyeres)')
for old in [c for c in G.children if c.name.startswith('fl_')]:
    old.destroy()


def fl_src(name):
    d = G.create(textDAT, 'fl_src_' + name)
    d.nodeX, d.nodeY = 3000, -200 - 60 * len([c for c in G.children if c.name.startswith('fl_src_')])
    d.text = open(FL + name + '.frag', encoding='utf-8').read().replace('//@COMMON', COMMON)
    return d


def fl_glsl(name, src, inputs, res, fmt='rgba32float', uniforms=False, x=3200, y=0):
    o = G.create(glslTOP, name)
    o.nodeX, o.nodeY = x, y
    for inp in inputs:                                   # appends to the next free input, in order
        inp.outputConnectors[0].connect(o)
    o.par.pixeldat = src.path
    o.par.format = fmt
    o.par.outputresolution = 'custom'
    o.par.resolutionw.expr, o.par.resolutionh.expr = res
    o.par.inputfiltertype = 'linear'
    if uniforms:
        o.seq.vec.numBlocks = max(len(UNIFORMS), o.seq.vec.numBlocks)
        for i, un in enumerate(UNIFORMS):
            getattr(o.par, 'vec%dname' % i).val = un
    return o


def fl_zero(name, res, x, y):
    z = G.create(constantTOP, name)
    z.nodeX, z.nodeY = x, y
    z.par.format = 'rgba32float'
    z.par.outputresolution = 'custom'
    z.par.resolutionw.expr, z.par.resolutionh.expr = res
    z.par.colorr = z.par.colorg = z.par.colorb = 0.0
    z.par.alpha = 1.0
    return z


fbed = G.create(scriptTOP, 'fl_bed')
fbed.nodeX, fbed.nodeY = 3200, 400
ftcb = synced(G, textDAT, 'fl_tops_callbacks', 'modules/galaxy/fluid_tops.py', 3000, 400)
fbed.par.callbacks = ftcb.path
fbed.par.format = 'rgba32float'
fmarks = G.create(scriptTOP, 'fl_marks')
fmarks.nodeX, fmarks.nodeY = 3200, 550
fmarks.par.callbacks = ftcb.path
fmarks.par.format = 'rgba32float'

vfb = G.create(feedbackTOP, 'fl_vel_fb')
vfb.nodeX, vfb.nodeY = 3200, 250
vfb.inputConnectors[0].connect(fl_zero('fl_zero_sim', SIM_RES, 3050, 250))
curl = fl_glsl('fl_curl', fl_src('curl'), [vfb], SIM_RES, x=3350, y=300)
vel = fl_glsl('fl_vel', fl_src('velocity'), [vfb, curl, fbed], SIM_RES, uniforms=True, x=3500, y=250)
div = fl_glsl('fl_div', fl_src('divergence'), [vel], SIM_RES, x=3650, y=250)
pfb = G.create(feedbackTOP, 'fl_p_fb')
pfb.nodeX, pfb.nodeY = 3650, 100
pfb.inputConnectors[0].connect(fl_zero('fl_zero_p', SIM_RES, 3500, 100))
jsrc = fl_src('jacobi')
prev = pfb
for i in range(20):
    prev = fl_glsl('fl_jacobi%02d' % i, jsrc, [prev, div], SIM_RES, x=3800 + 120 * i, y=100)
pfb.par.top = prev.path
proj = fl_glsl('fl_proj', fl_src('project'), [vel, prev], SIM_RES, x=6300, y=250)
vfb.par.top = proj.path

dfb = G.create(feedbackTOP, 'fl_dye_fb')
dfb.nodeX, dfb.nodeY = 6300, 450
dfb.inputConnectors[0].connect(fl_zero('fl_zero_dye', DYE_RES, 6150, 450))
dye = fl_glsl('fl_dye', fl_src('dye'), [dfb, proj], DYE_RES, fmt='rgba16float', uniforms=True, x=6450, y=450)
dfb.par.top = dye.path
wfb = G.create(feedbackTOP, 'fl_wave_fb')
wfb.nodeX, wfb.nodeY = 6300, 650
wfb.inputConnectors[0].connect(fl_zero('fl_zero_wave', DYE_RES, 6150, 650))
wave = fl_glsl('fl_wave', fl_src('wave'), [wfb, fbed], DYE_RES, uniforms=True, x=6450, y=650)
wave.par.inputfiltertype = 'nearest'
wfb.par.top = wave.path
view = fl_glsl('fl_view', fl_src('view'), [dye, wave, proj, fmarks],
               ('op.Config.par.Width', 'op.Config.par.Height'), fmt='rgba8fixed', uniforms=True, x=6650, y=450)

for c_ in list(tsel.inputConnectors):
    c_.disconnect()
tsel.inputConnectors[0].connect(add)
tsel.inputConnectors[1].connect(asel)
tsel.inputConnectors[2].connect(view)
tsel.par.index.expr = "{'lines': 0, 'attractor': 1, 'fluid': 2}.get(parent().par.Texture.eval(), 0)"
nm.par.fontalpha.expr = "0.85 if parent().par.Names and parent().par.Texture != 'fluid' else 0.0"
