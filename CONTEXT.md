# TDlive — context

Working document for Michael and Claude. Read this first when resuming. Sister project:
[td-experiment](https://github.com/MichaelKramerGuitar/td-experiment) ("8 Little Prayers": offline,
data-driven visuals), whose architecture and lessons this project reuses.

## 1. What this is

A TouchDesigner rig for **live solo guitar performance** with visuals that listen. The same rig rehearses and
records. Trio comes later; solo guitar is the focus.

Signal: Kemper → Focusrite 18i16 → TouchDesigner (direct from the interface, no Ableton needed to start).
Camera: webcam, with a "me in shot / pure shot" toggle.

## 2. Why (stated motives, kept explicit on purpose)

Two scorecards, kept separate so neither grades the other:

- **The art** (curiosity): audio-visual reactivity, data that matters to Michael, his synesthesia, his
  three-circle notation, visuals that "play duo" informed by song form. Judged by: did it teach something; would
  Michael stand behind it.
- **The delivery** (career): Instagram and YouTube as ways in; michaelkramerguitar.com (Bandzoogle) as the hub;
  growing the mailing list; material that helps with booking venues. Judged by process benchmarks Michael
  controls (pieces finished, clips posted, sign-ups per month), reviewed monthly, not view counts.

Live performance with listening visuals is where the two meet: it's both the richest art direction and the
most useful booking material.

## 3. Core ideas

- **Synesthesia palette** (`synesthesia/palette.yaml`): 17 spellings, Michael's own descriptions, starting colours
  to tune by eye. Representational, airy, never flat. The root of a chord dominates.
- **Spelling comes from the chart.** Audio gives a pitch class; the colour belongs to its spelling; the chart's
  harmony decides the spelling. This is what ties synesthesia, song form and notation into one system.
- **Charts** (`charts/`, `docs/NOTATION.md`): Michael's three-circle notation as data, a "book" we grow
  ourselves: originals first; standards when useful.
- **Notation as performer:** the three circles drawn live (outer ticks the bar, middle lights roots and melody,
  inner walks the form), so the visual knows where the tune is going and can anticipate, not just react.
- **Record the performance as data:** live recording at full quality is limited (TD Non-Commercial caps output at
  1280 px; recording + preview dropped TD to ~45 fps in td-experiment). So record audio, camera and control
  moves, and re-render the visuals offline at full quality. Rehearse stays fully live.

## 4. Roadmap

| Milestone | What | Done when |
|---|---|---|
| **M0 bootstrap** | repo, palette, chart schema, Gangster Flick sketch, tools + tests | ✅ this commit |
| **M1 skeleton** | Focusrite in (ASIO), webcam, Record / Rehearse with countdown, Space = start/stop, TDlive window (preview + buttons + input meter), modes Mirror + Ripples, the bus (`docs/LIVE_RIG.md`) | Michael can rehearse and record a take — ✅ 2026-11-20, end-to-end POC working (camera at 640x480) |
| **M2 harmony engine** | key-free (Roman numeral) charts; spelling in any key by letter arithmetic; chord-scales; weights (root > 3rd/7th > 5th > tensions); fretboard positions (`tools/harmony.py`) | ✅ 2026-11-21: blues + rhythm changes spell correctly in all 15 keys (tests) |
| **M3 form clock** | load a chart in TD; pick key + tempo in the TDlive window; count-off = bar 1; bar/section/chord clock on the bus; loops choruses | the visual knows which bar and chord it's on — ✅ 2026-11-21 (song COMP, musical count-in, Chart/Key buttons) |
| **M4 fretboard landscape** | Michael's image (below), first from the chart alone: wells at every chord-scale position, mass = weight, palette colours | the neck bends with the changes — ✅ 2026-11-21 v1 (60 fps; `docs/img/landscape_blues_F.jpg`) |
| **live-01** | tag: the rig ready for real takes (`docs/releases/live-01-fretboard-landscape.md`) | ✅ 2026-11-22 |
| **M5 listening** | pitch-class (chroma) analysis; played notes become dynamic masses ("melodic nodes"); later: key suggestion from the first bars | the landscape answers what's played |
| **M6 the circles** | three-circle notation drawn live from chart + audio | "playing duo" — v1 2026-11-23 (Notation mode, Stablemates) |
| **live-02** | tag: three circles + new window + click benchmarks (`docs/releases/live-02-three-circles.md`) | Michael's call |
| **Palette pass** | Michael hones the synesthesia colours by eye (pinned 2026-11-23) | soon |

### Michael's fretboard landscape (2026-11-21, his description)

A huge fretboard trailing off to the horizon in one-point perspective ("Star Wars credits"), implied by the
topology of a landscape more than drawn. The eye is at the bridge, looking toward the nut. The harmony of the
moment sits on it like planetary bodies: mass proportional to harmonic importance for grounding the harmony,
dynamic when a melodic node matters. Mass bends the surface the way a star bends spacetime (a basketball on a
trampoline). Nodes can be grips (chord shapes), but more often they're the whole harmonic topology of the
chord-scale, *from the perspective of* the passing root and melodic node - like his bird's-eye chord-scale
diagrams (every position of the scale over 19 frets), seen from the bridge instead.

Delivery track (in parallel, later): a page on the Bandzoogle site for 8 Little Prayers with the
process story and a sign-up; short cuts for Reels; Claude can help in the browser when we get there.

## 5. Decisions and open questions

- 2026-11-20: solo guitar first; audio straight from the Focusrite (USB ASIO, inputs 1+2 by default). (Check: can Ableton and TD share the
  interface at the same time on Windows? Only if needed.)
- 2026-11-20: Michael's Gangster Flick illustration is kept out of this public repo (his artwork; colours there
  are layer colours, not synesthesia).
- 2026-11-21: Blues and Rhythm Changes before Gangster Flick (hone the system on known forms first).
- 2026-11-21: charts are key-free (Roman numerals); Michael picks the key before the count-off; audio key
  suggestions later, never switching mid-tune.
- 2026-11-21: the fretboard landscape is the target visual for M4-M5 (it uses the same chart -> chord ->
  spelled chord-scale pipeline, so it ties the ideas together rather than adding one).
- Open: fixed vs relative do for harmony circles; colours for Cb/Fb/E#/B# and double sharps/flats (stand-in:
  enharmonic fallback); accent resolution.
- 2026-11-21: tuning is a Config choice, standard by default (alternate tunings are rare but real).
- 2026-11-21: chord-scale defaults approved; charts override chord by chord; charts can be subclassed
  (`extends` + `changes_patch`). Blues + rhythm changes versions approved as defaults.

## 6. Session log

- **2026-11-20 — session 1.** Bootstrap (M0): palette, chart schema, Gangster Flick sketch, chartlib + tests,
  palette swatch render.
- **2026-11-20 — session 1b.** Local folder linked to GitHub. M1 skeleton built by `scripts/build_live.py`
  (logic in `modules/show/`): Focusrite USB ASIO inputs 1+2, C920 webcam, Rehearse/Record with countdown,
  Space/Esc/R/H, take naming, TDlive window (opens on start). Test take OK (1280x720 60 fps MJPEG + stereo
  audio). Camera: Michael found the fix - a hand-made Video Device In at 640x480 works; the C920's HD modes
  stall at "Initializing..." (HD is a later task). Michael: "the e2e POC is working PERFECT". M1 done.
  Palette: Ab tuned redder.
  Next: M2 (palette live + pitch-class analysis); also tune Ripples response with real playing.
- **2026-11-21 — session 2.** Harmony engine (`tools/harmony.py`): Roman-numeral charts, letter-arithmetic
  spelling, chord-scales, weights, fretboard positions; `charts/blues_jazz.yaml`, `charts/rhythm_changes.yaml`;
  schema 0.2 (`changes_notation`, `default_key`); `render_fretboard.py`. Roadmap re-sequenced around
  Michael's fretboard landscape.
- **2026-11-21 — session 2b.** M3 form clock: configurable tunings, per-chord scale overrides, chart inheritance
  (`blues_basic` extends `blues_jazz`), `tools/formclock.py`; TD `song` COMP with engine (tables now / tones /
  positions + clock CHOP), musical count-in ending on bar 1, Chart + Key buttons. Next: M4 fretboard landscape.
- **2026-11-21 — session 2c.** M4 fretboard landscape v1: real fret spacing, eye behind the bridge looking to
  the nut, line terrain sunk by gaussian wells (depth ~ weight^2), palette colours, eased chord morphs, planets
  for root/3rd/7th, level glow + hit flash. Debugged TD 2025 instancing (default sphere; no premultiply on data
  textures). Next: Michael plays through it; then M5 listening (played notes as masses).
- **2026-11-21 — session 2d.** Michael's feedback on the landscape: perspective, materials and morph speed right;
  planets could be more radiant. Added: planet Clarity + Radiance; "Me" camera presence behind the land (ghost /
  outline / negative, brightness follows playing energy, tinted by the chord root, room cut + soft focus); click
  (visual window + preview dot, and/or audio tick to the interface; never recorded). Next: Michael's first real takes;
  then M5 listening.
- **2026-11-21 — session 2e.** TDlive window: take playback (Take + Play buttons, sound to the interface),
  tempo −/+ buttons, Me style button; panel now two rows. Michael ready for real takes.
- **2026-11-21 — session 2f.** First real takes: recording was choppy (MJPEG ~15 fps) -> Hap (~32 fps) and a
  steady 30 fps rig; Me brightened; playback sound via Audio Movie CHOP; Delete button (confirm, deferred file
  removal because TD holds played movies). TD froze once (Audio File In on a .mov stopped + cleared at once);
  after the forced restart, the build script restored everything that hadn't been saved.
- **2026-11-21 — session 2g.** Export button (ffmpeg -> 1080p H.264 mp4 in Exports/), Find Guitar Input, Me as a
  corner tile. Takes recorded silent audio: investigating (guitar is on Focusrite input 1; input numbering
  confirmed 0-based in TD).
- **2026-11-21 — session 2h.** Silent / missing takes solved: (1) selecting inputs by index picked the wrong
  input - Michael switched audio_in to all inputs by name; the build now picks the guitar by channel name and
  sends 2 channels to the recorder (20 channels made it silently write nothing); (2) Space in the network editor
  paused the timeline, which froze the show (Execute DAT frame callbacks + run(delayFrames) follow the timeline) -
  a real-clock watchdog now keeps it playing. Corner tile uses the outline look.
- **2026-11-22 — session 2i.** Release notes for `live-01-fretboard-landscape` (tag push is blocked from this
  session; Michael publishes it in the GitHub UI). Audible click fixed: `click/to_interface` Active was stuck in
  CONSTANT mode despite its expression (same for `playback_out`); build now forces expression mode. M5a: pitch
  follower (`modules/analysis/pitch.py`, McLeod NSDF, bus gains midi/clarity/freq; offline 0/49 errors MIDI 40–88)
  and the gesture whisp (`modules/landscape/gesture.py`: hand-position string/fret guess, palette colour, puffs that
  rise/drift/fade). Cook-loop lesson: Script CHOP memory via `scriptOp.store/fetch` re-cooks itself in a loop —
  keep per-op state in a module-level dict. Verified live: tracks Michael's line at ~0.95 clarity.
- **2026-11-23 — session 3.** Export progress (ffmpeg `-progress`: %, bar, ETA). TDlive window redesigned:
  header status line (moved out of the preview), captions, buttons sized to their widest text, grouped rows,
  state colours. Project "Michael's TouchDesigner Projects" created on claude.ai (these docs live there too).
  `charts/stablemates.yaml` from Michael's changes (spells exactly as written in Db; `9`/`13` qualities added).
  Click: Visual / Audio / Every buttons; click every beat, bar, or **form** (section tops + count into each
  section; big number = bar in section). Next: M6 circles mode, prototyped on Stablemates (Michael: how to draw
  the 14-bar A; melodic nodes).
- **2026-11-23 — session 3b.** M6 v1: Notation mode (three circles) — outer meter polygon + accents + beat light,
  circle of fifths with chord-scale nodes and harmony circles (outside major / inside minor, chord-tone polygons
  on fixed-do mini circles), played-note constellation, inner form shape with bar progress / zig-zag / play
  order. One GLSL pass over ~200 primitives from a Script TOP. Draft release notes `live-02-three-circles`.
  Pinned: palette pass soon.
- **2026-11-23 — session 3c.** Michael's answers: fixed do preferred, movable do as an option; the inner circle
  shows PHRASING (Stablemates A = 10 + 4, the 10 as 2 + 8 or 8 + 2); names optional (off by default); melodic
  nodes per bar (null = carry on). Schema: `form.sections[].phrasings`, `melody` (key-free degrees).
  `harmony.chord_function` names a node over a chord (9 -> 13, #9 over dominants). Stablemates split into A1
  (into the bridge on C7alt) / B / A2. Notation row in the window (mode-only row). Text TOP spec DAT lesson: it
  keeps its old text when the table empties and doesn't re-cook on table changes by itself (hide by font alpha;
  give the text param an expression that reads the table).
- **2026-11-25 — session 4.** Harmony Journey begins (concept + decisions live in the claude.ai project under
  `harmony-journey/`, out of git for now). Step 1 code: `tools/journey.py` (cohorts, key torus, perfect-cadence
  and plagal families spelled toward their targets, related ii, tension dials). Charts: All The Things You Are,
  Along Came Betty (Michael's changes, his hearing in `analysis`). Harmony: slash chords (`I/3`), -9, maj13, 7b9.
  Performance meter (Song › Meter, METER button). Too-wide rows shorten the chart title.
- **2026-11-25 — session 4b.** Endings: chart `endings` (last chorus only), armed hands-free with the End key
  (E / PageDown: Bluetooth page-turner pedals send those) -> the last chord rings a bar, then the take stops.
  Verified live on ATTYA (bar 36 = Abmaj7, then idle). Next: Journey step 2, the "Solar" mode.
- **2026-11-25 — session 4c.** Journey step 2, first picture: **Harmony Galaxy** mode (Michael renamed it from
  "Solar", a standard he'll chart). Key stars placed by fifths distance from home in a gravity landscape (home
  and its cohorts dig valleys, the further out the higher), the local tonic (from Michael's `analysis` roles via
  `journey.journey_plan`) deepens its valley and carries 7 diatonic planets; secondary chords orbit as moons; a
  traveller comet with a trail, and a tether home that sags when slack and pulls taut/red with tension. Drawn
  with the notation shader (layers: grid at half resolution). Mode row now per mode (Galaxy: camera view, grid,
  tether, key names, caption). Lesson: a Text TOP expression with no changing reference never re-evaluates
  (add absTime.frame).
- **2026-11-25 — session 4d.** Galaxy body cam (Michael: the melody traveller is the protagonist): the camera
  rides just behind and above the traveller, looking along its smoothed heading, wide lens (Body Cam Field Of
  View, 62). Camera View now cycles Body cam / Follow / From above; body cam is the default. Rigid attachment
  (only the heading smoothed) keeps the traveller in the lower middle; sizes capped up close.
- **2026-11-25 — session 4e.** Galaxy performance: the grid was ~1,100 segments that every pixel of BOTH passes
  looped over. Now each layer has its own rows in the primitive texture (draw.frag: uLayer picks rows 3*layer..),
  the grid is built with numpy (13 x 26), depth-faded, drawn at 0.25 resolution (Gridres). Measured with grid
  on: 30 fps; GPU ~6 ms grid + ~10 ms bodies; Script TOP ~5 ms. Lesson: the per-pixel primitive loop costs
  (pixels x primitives) - keep lists short per pass; GPU instanced quads would be the next step if needed.
  Protagonist: comet or **melody whisp** (pitch follower -> palette-coloured puffs born at the traveller, higher
  for higher notes, joined in order, left behind as a wake).
- **2026-11-26 — session 5.** Textures begin (claude.ai project `harmony-journey/TEXTURES.md`). Offline prototype
  (`tools/attractors.py`, `scripts/proto_attractors.py`): 7 attractors normalised, tension blends a calm laminar
  orbit into each strange attractor (Lorenz all-or-nothing), one attractor per key role (home Aizawa, Coltrane
  cohort Halvorsen/TSCUS, minor-third cohort Four-Wing, near Thomas, far Lorenz), particles stream key to key and
  dissolve onto the new attractor, a quarter stay home. Then the **Attractor texture** in Harmony Galaxy: GPU
  particles (32k; sim = GLSL TOP in a feedback loop, generated by `scripts/gen_attractor_glsl.py` from the same
  Python; seeds from `modules/galaxy/attractor_seeds.npy`), instanced camera-facing billboards rendered through a
  TD camera matched each frame to the galaxy's own projection, points / trails (feedback fade) / both, with the
  stars or abstract. Window: TEXTURE, PARTICLES, SHOW. Measured: sim ~0.1 ms, render 1-7 ms, ~28 fps in body cam
  with everything on. Lessons: `par['name'] = x` doesn't set built-in pars (use getattr(...).val); a loop
  variable named like an operator variable silently breaks later wiring; size GLSL uniform blocks via
  op.seq.vec.numBlocks first.
- **2026-11-27 — session 6.** Fluid texture, first pass (Michael's two images: harmony as the creek bed the
  melody flows over / harmony as the medium's properties the melody pushes against; looks: ink first, then water
  surface and smoke; current and pings configurable; flat top-down first, draped later). GPU stable fluids in
  `modules/galaxy/fluid/*.frag` (build inlines `common.glsl`): velocity (advect + vorticity confinement + current
  + bed + traveller push + note bursts), divergence, 20 Jacobi pressure passes, projection, ink, the bat's pings
  (wave equation, speed ~ sqrt(depth of the harmony bed)), view (ripple refraction), star marks. Python:
  `fluid_tops.py` (bed height map from the galaxy wells, marks), `world.fluid_update` (uniforms, note onsets,
  pings every / long / off, current none / pull home / the form). ~30 fps; fluid GPU ~2 ms. Lessons: a new GLSL
  TOP offers scripts only 3 input connectors; in a texture where nothing on screen pulls the world Script TOP it
  doesn't cook (cook it from the frame tick); keep cross-module state in COMP storage. Image 2 (medium) next.
- **2026-11-27 — session 6b.** Beatrice (Sam Rivers) from Michael's changes, nodes and hearing (16 bars, F).
  "Gestural function" (Michael): root motion and voice leading carry function when the quality doesn't (Dameron's
  Lady Bird turnaround; Beatrice's Gbmaj7#11 -> Fmaj7, Ebmaj7 -> D-7, the D-7 C-7 Bb-7 A-7 line):
  `journey.gestural(chord, next, prev)` -> subV / V / line, softened when not a dominant 7. Fluid: a drain into
  home's whirlpool (the pressure solve targets edge sources + a home sink) and background ink: off / grey / a
  muted, slowly shifting shade of the current chord root.

