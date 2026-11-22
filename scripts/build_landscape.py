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
    pg.appendFloat('Contrast', label='Mass Contrast (depth ~ weight^n)')
    pg.appendFloat('Ease', label='Chord Morph Speed')
    pg.appendFloat('Brightness', label='Line Brightness')
    pg.appendFloat('Planetsize', label='Planet Size')
    pg.appendFloat('Planetmin', label='Planets From Weight (0.6 = root, 3rd, 7th)')
    pg.appendFloat('Planetclarity', label='Planet Clarity (0 = radiant cloud, 1 = crisp)')
    pg.appendFloat('Planetradiance', label='Planet Radiance (halo)')
    pg3 = page(L, 'Me')
    pg3.appendMenu('Mestyle', label='Style')
    L.par.Mestyle.menuNames = ['ghost', 'outline', 'negative']
    L.par.Mestyle.menuLabels = ['Ghost (soft light)', 'Outline (traced edge)', 'Negative']
    pg3.appendFloat('Meamount', label='Brightness')
    pg3.appendFloat('Mereact', label='Follows Playing (0 = always on, 1 = only when playing)')
    pg3.appendFloat('Mefade', label='Fade After Playing (s)')
    pg3.appendToggle('Metint', label='Tint With Chord Root Colour')
    pg3.appendFloat('Mecut', label='Cut The Room (black level)')
    pg3.appendFloat('Mefocus', label='Focus (vignette: smaller = only the centre)')
    pg2 = page(L, 'Camera')
if not has(L, 'Gesture'):                                  # melodic gesture whisp over the neck
    pg5 = page(L, 'Gesture')
    pg5.appendToggle('Gesture', label='Melodic Gesture Whisp')
    pg5.appendFloat('Gesturetrail', label='Trail Length (s)')
    pg5.appendFloat('Gesturesize', label='Whisp Size')
    pg5.appendFloat('Gesturerise', label='Rise')
    pg5.appendFloat('Gesturedrift', label='Drift (zephyr)')
    pg5.appendFloat('Gestureclarity', label='Pitch Confidence Needed (0..1)')
    pg5.appendFloat('Gesturesoft', label='Softness')
    for k, v in (('Gesture', True), ('Gesturetrail', 3.0), ('Gesturesize', 0.11), ('Gesturerise', 0.35),
                 ('Gesturedrift', 0.3), ('Gestureclarity', 0.8), ('Gesturesoft', 0.6)):
        L.par[k] = v
        L.par[k].default = v
if not has(L, 'Meplace'):                                   # me as a corner tile (like a speaker on a call)
    pg4 = page(L, 'Me')
    pg4.appendMenu('Meplace', label='Placement')
    L.par.Meplace.menuNames = ['background', 'top_left', 'top_right', 'bottom_left', 'bottom_right']
    L.par.Meplace.menuLabels = ['Background (behind the land)', 'Tile top left', 'Tile top right',
                                'Tile bottom left', 'Tile bottom right']
    pg4.appendFloat('Mesize', label='Tile Size (fraction of width)')
    pg4.appendMenu('Metilelook', label='Tile Look')
    L.par.Metilelook.menuNames = ['camera', 'styled']
    L.par.Metilelook.menuLabels = ['Camera (natural)', 'Styled (same as background style)']
    pg4.appendFloat('Metileopacity', label='Tile Opacity')
    L.par.Mesize, L.par.Mesize.default = 0.26, 0.26
    L.par.Metilelook, L.par.Metilelook.default = 'styled', 'styled'
    L.par.Metileopacity, L.par.Metileopacity.default = 1.0, 1.0
    pg2.appendFloat('Camheight', label='Eye Height')
    pg2.appendFloat('Camback', label='Eye Behind Bridge')
    pg2.appendFloat('Lookdown', label='Look Point Below Neck')
    pg2.appendFloat('Fov', label='Field Of View')
    for k, v in (('Depth', 0.9), ('Spread', 1.0), ('Contrast', 2.0), ('Ease', 0.12), ('Brightness', 0.9), ('Planetsize', 0.14),
                 ('Planetmin', 0.6), ('Planetclarity', 0.55), ('Planetradiance', 0.5),
                 ('Meamount', 0.9), ('Mereact', 0.7), ('Mefade', 1.5), ('Metint', True), ('Mecut', 0.16), ('Mefocus', 0.75), ('Camheight', 3.2), ('Camback', 7.0), ('Lookdown', 3.0), ('Fov', 44)):
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
field.par.vec0valuez.expr = "0.5 * parent().par.Spread"
field.par.vec0valuew.expr = "0.024 * parent().par.Spread"
field.par.vec1name = 'uK'
field.par.vec1valuex.expr = 'parent().par.Contrast'
field.par.premultrgbbyalpha = False                      # data, not colour: never premultiply

fb = ensure(L, feedbackTOP, 'feedback', 350, 100)
smooth = ensure(L, crossTOP, 'smooth', 500, 0)            # eases the surface from chord to chord
smooth.inputConnectors[0].connect(fb)
smooth.inputConnectors[1].connect(field)
smooth.par.cross.expr = '1 - (1 - parent().par.Ease) ** (60.0 / max(1, project.cookRate))'   # same speed at any fps
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
line_geo('terrain', 420, 31, 'cols', m_ter, 1100, 300)       # long lines down the neck
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
plx.par.premultrgbbyalpha = False
plx.par.vec0name = 'uY'
plx.par.vec0valuex, plx.par.vec0valuey = YMIN, YMAX
plx.par.vec1name = 'uWorld'
plx.par.vec1valuex, plx.par.vec1valuey = STRING_W, NECK_L
plx.par.vec1valuez.expr = 'parent().par.Depth'
plx.par.vec1valuew.expr = 'parent().par.Planetsize'
plx.par.vec0valuez.expr = 'parent().par.Planetmin'
pmat = ensure(L, constantMAT, 'mat_planets', 900, -150)
pmat.par.colorr = pmat.par.colorg = pmat.par.colorb = 1.0
old_pl = L.op('planets')
if old_pl is not None:                                     # always fresh (a broken instancing state can stick)
    old_pl.destroy()
pl = L.create(geometryCOMP, 'planets')
pl.nodeX, pl.nodeY = 1100, -150
for c in list(pl.children):
    c.destroy()
ball = pl.create(sphereSOP, 'ball')                       # default sphere: custom type/rows broke instancing
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

def render_top(name, geos, x, y, bg_alpha):
    r = ensure(L, renderTOP, name, x, y)
    r.par.outputresolution = 'custom'
    r.par.resolutionw.expr, r.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
    r.par.camera = cam.path
    r.par.geometry = ' '.join(g.path for g in geos)
    r.par.bgcolorr, r.par.bgcolorg, r.par.bgcolorb, r.par.bgcolora = 0.012, 0.014, 0.022, bg_alpha
    if 'antialias' in [p.name for p in r.pars()]:
        r.par.antialias = 'aa8' if 'aa8' in r.par.antialias.menuNames else r.par.antialias.eval()
    return r


rnd = render_top('render', (L.op('terrain'), L.op('frets'), L.op('strings')), 1500, 50, 1.0)
blur = ensure(L, blurTOP, 'glow_blur', 1650, -50)
blur.inputConnectors[0].connect(rnd)
blur.par.size = 12
glow = ensure(L, compositeTOP, 'glow', 1800, 50)
glow.inputConnectors[0].connect(rnd)
glow.inputConnectors[1].connect(blur)
glow.par.operand = 'add'

# planets: rendered on their own so they can be crisp or a radiant cloud (Clarity) with a halo (Radiance)
rp = render_top('render_planets', (pl,), 1500, -250, 0.0)
psoft = ensure(L, blurTOP, 'planet_soft', 1650, -250)
psoft.inputConnectors[0].connect(rp)
psoft.par.size.expr = '2 + 26 * (1 - parent().par.Planetclarity)'
pmix = ensure(L, crossTOP, 'planet_clarity', 1800, -250)
pmix.inputConnectors[0].connect(rp)
pmix.inputConnectors[1].connect(psoft)
pmix.par.cross.expr = '1 - parent().par.Planetclarity'
phalo = ensure(L, blurTOP, 'planet_halo', 1650, -400)
phalo.inputConnectors[0].connect(rp)
phalo.par.size = 36
phl = ensure(L, levelTOP, 'planet_halo_gain', 1800, -400)
phl.inputConnectors[0].connect(phalo)
phl.par.brightness1.expr = '0.9 * parent().par.Planetradiance'
pall = ensure(L, compositeTOP, 'planets_lit', 1950, -300)
pall.inputConnectors[0].connect(pmix)
pall.inputConnectors[1].connect(phl)
pall.par.operand = 'add'

# me: the camera as light behind the land, appearing with the energy of the playing
energy = ensure(L, lagCHOP, 'energy', 1500, -600)            # quick to appear, lingers after the playing stops
lvl_sel = ensure(L, selectCHOP, 'level_in', 1350, -600)
lvl_sel.par.chop = op.Analysis.op('out').path
lvl_sel.par.channames = 'level'
energy.inputConnectors[0].connect(lvl_sel)
energy.par.lag1 = 0.05
energy.par.lag2.expr = 'parent().par.Mefade'
mcam = ensure(L, selectTOP, 'me_cam', 1350, -800)
mcam.par.top = op.Sources.op('cam').path
mmono = ensure(L, monochromeTOP, 'me_mono', 1500, -800)
mmono.inputConnectors[0].connect(mcam)
# ghost: soft, lifted luminance
gb = ensure(L, blurTOP, 'me_ghost_blur', 1650, -700)
gb.inputConnectors[0].connect(mmono)
gb.par.size = 6
gl = ensure(L, levelTOP, 'me_ghost', 1800, -700)
gl.inputConnectors[0].connect(gb)
gl.par.blacklevel.expr = 'parent().par.Mecut'
gl.par.contrast = 1.4
# outline: traced edges
ed = ensure(L, edgeTOP, 'me_edge', 1650, -850)
ed.inputConnectors[0].connect(mmono)
eb = ensure(L, blurTOP, 'me_outline', 1800, -850)
eb.inputConnectors[0].connect(ed)
eb.par.size = 2
eg = ensure(L, levelTOP, 'me_outline_gain', 1950, -850)
eg.inputConnectors[0].connect(eb)
eg.par.brightness1 = 3.0
eg.par.blacklevel.expr = 'parent().par.Mecut * 0.5'
# negative: inverted luminance, darkest parts glow
ng = ensure(L, levelTOP, 'me_negative', 1650, -1000)
ng.inputConnectors[0].connect(gb)
ng.par.invert = 1.0
ng.par.blacklevel.expr = 'parent().par.Mecut + 0.15'
msw = ensure(L, switchTOP, 'me_style', 2100, -850)
msw.inputConnectors[0].connect(gl)
msw.inputConnectors[1].connect(eg)
msw.inputConnectors[2].connect(ng)
msw.par.index.expr = 'parent().par.Mestyle.menuIndex'
tint = ensure(L, constantTOP, 'me_tint', 2100, -1000)
tint.par.resolutionw, tint.par.resolutionh = 8, 8
for ch, col in (('colorr', 'r'), ('colorg', 'g'), ('colorb', 'b')):
    tint.par[ch].expr = ("float(op.Song.op('tones')[1, '%s'] or 1) * 0.8 + 0.2 if parent().par.Metint and "
                         "op.Song.op('tones').numRows > 1 else 0.85") % col
mt = ensure(L, compositeTOP, 'me_tinted', 2250, -900)
mt.inputConnectors[0].connect(msw)
mt.inputConnectors[1].connect(tint)
mt.par.operand = 'multiply'
mt.par.size = 'input1' if 'input1' in mt.par.size.menuNames else mt.par.size.eval()
old_v = L.op('me_vignette')
if old_v is not None and old_v.OPType != 'glslTOP':
    old_v.destroy()
for n in ('me_vignette_inv',):
    if L.op(n) is not None:
        L.op(n).destroy()
vpx = synced(L, textDAT, 'vignette_frag', 'modules/landscape/vignette.frag', 2250, -1200)
vig = ensure(L, glslTOP, 'me_vignette', 2250, -1050)       # centre-weighted: the room fades toward the edges
vig.par.pixeldat = vpx.path
vig.par.outputresolution = 'custom'
vig.par.resolutionw.expr, vig.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
vig.par.vec0name = 'uV'
vig.par.vec0valuex.expr = 'parent().par.Mefocus'
vig.par.vec0valuey.expr = 'op.Config.par.Width / op.Config.par.Height'
vig.par.vec0valuez = 0.55
vigi = vig
mv = ensure(L, compositeTOP, 'me_focused', 2400, -900)
mv.inputConnectors[0].connect(mt)
mv.inputConnectors[1].connect(vigi)
mv.par.operand = 'multiply'
me = ensure(L, levelTOP, 'me', 2550, -900)
me.inputConnectors[0].connect(mv)
me.par.brightness1.expr = ("0 if parent().par.Meplace != 'background' else "
                           "parent().par.Meamount * (1 - parent().par.Mereact + parent().par.Mereact * "
                           "min(1, op('energy')['level'] * 3.0))")

# tile: me in a corner, over the land
tsrc = ensure(L, switchTOP, 'tile_source', 2250, -1300)
tsrc.inputConnectors[0].connect(mcam)
tsrc.inputConnectors[1].connect(mt)
tsrc.par.index.expr = "parent().par.Metilelook.menuIndex"
tile_lvl = ensure(L, levelTOP, 'tile_look', 2400, -1300)
tile_lvl.inputConnectors[0].connect(tsrc)
tile_lvl.par.opacity.expr = ("parent().par.Metileopacity if parent().par.Meplace != 'background' "
                             "and op.Show.par.Camerainshot else 0")
frame = ensure(L, constantTOP, 'tile_frame', 2400, -1450)  # thin light border behind the tile
frame.par.resolutionw, frame.par.resolutionh = 16, 9
frame.par.colorr = frame.par.colorg = frame.par.colorb = 0.75
frame.par.alpha.expr = "0.55 if parent().par.Meplace != 'background' and op.Show.par.Camerainshot else 0"
CORNER = ("{'top_left': (-1, 1), 'top_right': (1, 1), 'bottom_left': (-1, -1), 'bottom_right': (1, -1)}"
          ".get(parent().par.Meplace.eval(), (0, 0))")
for name_, src_, grow in (('tile_border', frame, 1.012), ('tile', tile_lvl, 1.0)):
    t = ensure(L, transformTOP, name_, 2550, -1300 if name_ == 'tile' else -1450)
    t.inputConnectors[0].connect(src_)
    t.par.outputresolution = 'custom'
    t.par.resolutionw.expr, t.par.resolutionh.expr = 'op.Config.par.Width', 'op.Config.par.Height'
    t.par.extend = 'zero'
    t.par.sx.expr = 'parent().par.Mesize * %s' % grow
    t.par.sy.expr = 'parent().par.Mesize * %s' % grow            # cam is already fitted to the format
    m = 0.03
    t.par.tx.expr = "%s[0] * (0.5 - parent().par.Mesize / 2 - %s)" % (CORNER, m)
    t.par.ty.expr = ("%s[1] * (0.5 - parent().par.Mesize / 2 - %s * op.Config.par.Width / op.Config.par.Height)"
                     % (CORNER, m))
tile_all = ensure(L, compositeTOP, 'tile_all', 2700, -1350)
tile_all.inputConnectors[0].connect(L.op('tile'))
tile_all.inputConnectors[1].connect(L.op('tile_border'))
tile_all.par.operand = 'over'

# melodic gesture whisp: puffs from the pitch follower, instanced, soft and glowing
gcb = synced(L, textDAT, 'gesture_callbacks', 'modules/landscape/gesture.py', 1350, -1600)
gest = ensure(L, scriptCHOP, 'gesture', 1500, -1600)
gest.par.callbacks = gcb.path
wmat = ensure(L, constantMAT, 'mat_whisp', 1650, -1700)
wmat.par.colorr = wmat.par.colorg = wmat.par.colorb = 1.0
wmat.par.blending = True
wmat.par.srcblend, wmat.par.destblend = 'one', 'one'
wmat.par.depthtest = False
old_w = L.op('whisp')
if old_w is not None:
    old_w.destroy()
wg = L.create(geometryCOMP, 'whisp')
wg.nodeX, wg.nodeY = 1650, -1600
for c in list(wg.children):
    c.destroy()
wb = wg.create(sphereSOP, 'puff')                          # default sphere (custom types broke instancing)
wb.render = wb.display = True
wg.par.instancing = True
wg.par.instanceop = gest.path
wg.par.instancetx, wg.par.instancety, wg.par.instancetz = 'tx', 'ty', 'tz'
wg.par.instancesx = wg.par.instancesy = wg.par.instancesz = 's'
wg.par.instancecolorop = gest.path
wg.par.instancer, wg.par.instanceg, wg.par.instanceb = 'r', 'g', 'b'
wg.par.material = wmat.path
rw = render_top('render_whisp', (wg,), 1800, -1600, 0.0)
wsoft = ensure(L, blurTOP, 'whisp_soft', 1950, -1600)
wsoft.inputConnectors[0].connect(rw)
wsoft.par.size.expr = '3 + 30 * parent().par.Gesturesoft'
wmix = ensure(L, compositeTOP, 'whisp_lit', 2100, -1600)
wmix.inputConnectors[0].connect(rw)
wmix.inputConnectors[1].connect(wsoft)
wmix.par.operand = 'add'
wgain = ensure(L, levelTOP, 'whisp_out', 2250, -1600)
wgain.inputConnectors[0].connect(wmix)
wgain.par.opacity.expr = '1 if parent().par.Gesture else 0'

final_l = ensure(L, compositeTOP, 'landscape_all', 2550, 0)
final_l.inputConnectors[0].connect(glow)
final_l.inputConnectors[1].connect(pall)
final_l.inputConnectors[2].connect(me)
final_l.inputConnectors[3].connect(wgain)
final_l.par.operand = 'add'
with_tile = ensure(L, compositeTOP, 'with_tile', 2700, 0)
with_tile.inputConnectors[0].connect(L.op('tile_all'))
with_tile.inputConnectors[1].connect(final_l)
with_tile.par.operand = 'over'
lout = ensure(L, outTOP, 'out1', 2850, 0)
lout.inputConnectors[0].connect(with_tile)
landscape_report = {'masses': masses.width, 'field': [field.width, field.height],
                    'errors': {o.path: o.errors() for o in L.findChildren(depth=None) if o.errors()},
                    'warnings': {o.path: o.warnings() for o in L.findChildren(depth=None) if o.warnings()}}
