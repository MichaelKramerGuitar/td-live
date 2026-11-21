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
| **M5 listening** | pitch-class (chroma) analysis; played notes become dynamic masses ("melodic nodes"); later: key suggestion from the first bars | the landscape answers what's played |
| **M6 the circles** | three-circle notation drawn live from chart + audio | "playing duo" |

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
