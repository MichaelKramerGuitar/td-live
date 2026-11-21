# Build the "Fretboard landscape" mode (visuals/landscape). Run by build_live.py (needs its helpers:
# ensure, synced, page, has). Michael's image: a huge fretboard trailing to the horizon, seen from the bridge
# toward the nut; the chord-scale of the moment as masses that bend the surface (root heaviest).
#
#   song/positions (every fretboard position of the current chord-scale, with weight + palette colour)
#     -> masses / mass_colors (Script TOPs, one pixel per position)
#     -> field (GLSL TOP: well depth + colour over the whole neck)  -> smooth (eases between chords) = field_s
#     -> terrain / frets / strings (line grids, GLSL MAT lays them on the neck and sinks them into the wells)
#     -> planets (instanced spheres sitting in the wells)  -> cam -> render -> glow -> out1

V = op('/project1/visuals')
L = ensure(V, baseCOMP, 'landscape', 0, -400)
if not has(L, 'Flip'):
    pg = page(L, 'Landscape')
    pg.appendToggle('Flip', label='Low String On The Right')
    pg.appendFloat('Depth', label='Well Depth')
    pg.appendFloat('Spread', label='Well Width')
    pg.appendFloat('Ease', label='Chord Morph Speed')
    pg.appendFloat('Brightness', label='Line Brightness')
    pg.appendFloat('Planetsize', label='Planet Size')
    pg2 = page(L, 'Camera')
    pg2.appendFloat('Camheight', label='Eye Height')
    pg2.appendFloat('Camback', label='Eye Behind Bridge')
    pg2.appendFloat('Lookdown', label='Look Point Below Neck')
    pg2.appendFloat('Fov', label='Field Of View')
    for k, v in (('Depth', 1.6), ('Spread', 1.0), ('Ease', 0.12), ('Brightness', 0.9), ('Planetsize', 0.28),
                 ('Camheight', 2.4), ('Camback', 2.5), ('Lookdown', 2.0), ('Fov', 52)):
        L.par[k] = v
        L.par[k].default = v

YMIN, YMAX, STRING_W, NECK_L = -0.05, 0.70, 1.0, 40.0
UY = "%s, %s" % (YMIN, YMAX)

masses = ensure(L, scriptTOP, 'masses', 0, 0)
mcols = ensure(L, scriptTOP, 'mass_colors', 0, -150)
cb = synced(L, textDAT, 'masses_callbacks', 'modules/landscape/masses.py', -200, -75)
for t in (masses, mcols):
    t.par.callbacks = cb.path
    t.par.format = 'rgba32float'

field_px = synced(L, textDAT, 'field_frag', 'modules/landscape/field.frag', 150, 150)
field = ensure(L, glslTOP, 'field', 200, 0)
field.inputConnectors[0].connect(masses)
field.inputConnectors[1].connect(mcols)
field.par.pixeldat = field_px.path
field.par.outputresolution = 'custom'
field.par.resolutionw, field.par.resolutionh = 96, 1024
field.par.format = 'rgba32float'
field.par.vec0name = 'uY'
field.par.vec0valuex, field.par.vec0valuey = YMIN, YMAX
field.par.vec0valuez.expr = "0.42 * parent().par.Spread"
field.par.vec0valuew.expr = "0.016 * parent().par.Spread"

fb = ensure(L, feedbackTOP, 'feedback', 350, 100)
smooth = ensure(L, crossTOP, 'smooth', 500, 0)            # eases the surface from chord to chord
smooth.inputConnectors[0].connect(fb)
smooth.inputConnectors[1].connect(field)
smooth.par.cross.expr = 'parent().par.Ease'
smooth.par.format = 'rgba32float' if 'rgba32float' in smooth.par.format.menuNames else smooth.par.format.eval()
fb.inputConnectors[0].connect(field)
fb.par.top = smooth.path
field_s = ensure(L, nullTOP, 'field_s', 650, 0)
field_s.inputConnectors[0].connect(smooth)

vert = synced(L, textDAT, 'land_vert', 'modules/landscape/land.vert', 650, 300)
frag = synced(L, textDAT, 'land_frag', 'modules/landscape/land.frag', 650, 200)


def land_mat(name, smin, smax, fretmode, base, bright, opacity, x, y):
    m = ensure(L, glslMAT, name, x, y)
    m.par.vdat = vert.path
    m.par.pdat = frag.path
    m.par.sampler0name = 'sField'
    m.par.sampler0top = field_s.path
    m.par.vec0name = 'uMap'
    m.par.vec0valuex, m.par.vec0valuey, m.par.vec0valuez = smin, smax, fretmode
    m.par.vec0valuew.expr = 'op.Song.par.Frets'
    m.par.vec1name = 'uY'
    m.par.vec1valuex, m.par.vec1valuey = YMIN, YMAX
    m.par.vec2name = 'uWorld'
    m.par.vec2valuex, m.par.vec2valuey = STRING_W, NECK_L
    m.par.vec2valuez.expr = 'parent().par.Depth'
    m.par.vec3name = 'uLook'
    m.par.vec3valuex.expr = 'parent().par.Brightness * %s' % bright
    m.par.vec3valuey.expr = "op.Analysis.op('out')['level']"
    m.par.vec3valuez.expr = "op.Analysis.op('out')['hit']"
    m.par.vec3valuew = opacity
    m.par.vec4name = 'uBase'
    m.par.vec4valuex, m.par.vec4valuey, m.par.vec4valuez = base
    m.par.blending = True
    m.par.srcblend, m.par.destblend = 'sa', 'one'          # additive glow
    m.par.depthtest = False
    return m


def line_geo(name, rows, cols, surftype, mat, x, y):
    g = ensure(L, geometryCOMP, name, x, y)
    for c in list(g.children):
        if c.name not in ('grid',):
            c.destroy()
    grid = ensure(g, gridSOP, 'grid', 0, 0)
    grid.par.orient = 'xy'
    grid.par.sizex = grid.par.sizey = 1
    grid.par.rows, grid.par.cols = rows, cols
    grid.par.type = 'poly'                                  # separate polylines, drawn as lines
    grid.par.surftype = surftype
    grid.render = grid.display = True
    g.par.material = mat.path
    return g


m_ter = land_mat('mat_terrain', -0.5, 5.5, 0, (0.20, 0.25, 0.34), 0.55, 0.85, 900, 300)
m_fret = land_mat('mat_frets', -0.35, 5.35, 1, (0.30, 0.30, 0.34), 0.75, 0.9, 900, 150)
m_str = land_mat('mat_strings', 0.0, 5.0, 0, (0.55, 0.55, 0.60), 1.0, 1.0, 900, 0)
line_geo('terrain', 420, 43, 'cols', m_ter, 1100, 300)       # long lines down the neck
fr = line_geo('frets', 2, 40, 'rows', m_fret, 1100, 150)     # one line per fret (rows set below)
fr.op('grid').par.rows.expr = 'op.Song.par.Frets + 1'
line_geo('strings', 420, 6, 'cols', m_str, 1100, 0)          # the six strings, brighter

pl_px = synced(L, textDAT, 'planets_frag', 'modules/landscape/planets.frag', 650, -250)
plx = ensure(L, glslTOP, 'planet_xf', 800, -150)
plx.inputConnectors[0].connect(masses)
plx.inputConnectors[1].connect(field_s)
plx.par.pixeldat = pl_px.path
plx.par.outputresolution = 'custom'
plx.par.resolutionw.expr = "op('masses').width"
plx.par.resolutionh = 1
plx.par.format = 'rgba32float'
plx.par.vec0name = 'uY'
plx.par.vec0valuex, plx.par.vec0valuey = YMIN, YMAX
plx.par.vec1name = 'uWorld'
plx.par.vec1valuex, plx.par.vec1valuey = STRING_W, NECK_L
plx.par.vec1valuez.expr = 'parent().par.Depth'
plx.par.vec1valuew.expr = 'parent().par.Planetsize'
pmat = ensure(L, constantMAT, 'mat_planets', 900, -150)
pmat.par.colorr = pmat.par.colorg = pmat.par.colorb = 1.0
pl = ensure(L, geometryCOMP, 'planets', 1100, -150)
for c in list(pl.children):
    if c.name != 'ball':
        c.destroy()
ball = ensure(pl, sphereSOP, 'ball', 0, 0)
ball.par.type = 'polygon'
ball.par.rows, ball.par.cols = 10, 14
ball.render = ball.display = True
pl.par.instancing = True
pl.par.instanceop = plx.path
pl.par.instancetx, pl.par.instancety, pl.par.instancetz = 'r', 'g', 'b'
pl.par.instancesx = pl.par.instancesy = pl.par.instancesz = 'a'
pl.par.instancecolorop = mcols.path
pl.par.instancer, pl.par.instanceg, pl.par.instanceb = 'r', 'g', 'b'
pl.par.material = pmat.path

cam = ensure(L, cameraCOMP, 'cam', 1300, 100)
tgt = ensure(L, nullCOMP, 'target', 1300, -50)
cam.par.tx = 0
cam.par.ty.expr = 'parent().par.Camheight'
cam.par.tz.expr = 'parent().par.Camback'
tgt.par.tx, tgt.par.tz = 0, -NECK_L * 0.62
tgt.par.ty.expr = '-parent().par.Lookdown'
cam.par.lookat = tgt.path
cam.par.fov.expr = 'parent().par.Fov'
cam.par.near, cam.par.far = 0.05, 200

rnd = ensure(L, renderTOP, 'render', 1500, 50)
rnd.par.outputresolution = 'custom'
rnd.par.resolutionw.expr, rnd.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
rnd.par.camera = cam.path
rnd.par.geometry = ' '.join(g.path for g in (L.op('terrain'), L.op('frets'), L.op('strings'), pl))
rnd.par.bgcolorr, rnd.par.bgcolorg, rnd.par.bgcolorb, rnd.par.bgcolora = 0.012, 0.014, 0.022, 1.0
if 'antialias' in [p.name for p in rnd.pars()]:
    rnd.par.antialias = 'aa8' if 'aa8' in rnd.par.antialias.menuNames else rnd.par.antialias.eval()
blur = ensure(L, blurTOP, 'glow_blur', 1650, -50)
blur.inputConnectors[0].connect(rnd)
blur.par.size = 12
glow = ensure(L, compositeTOP, 'glow', 1800, 50)
glow.inputConnectors[0].connect(rnd)
glow.inputConnectors[1].connect(blur)
glow.par.operand = 'add'
lout = ensure(L, outTOP, 'out1', 1950, 50)
lout.inputConnectors[0].connect(glow)
landscape_report = {'masses': masses.width, 'field': [field.width, field.height],
                    'errors': {o.path: o.errors() for o in L.findChildren(depth=None) if o.errors()},
                    'warnings': {o.path: o.warnings() for o in L.findChildren(depth=None) if o.warnings()}}
