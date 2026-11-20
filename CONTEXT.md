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
| **M1 skeleton** | Focusrite in (ASIO), webcam, Record / Rehearse with countdown, Space = start/stop, TDlive window (preview + buttons + input meter), modes Mirror + Ripples, the bus (`docs/LIVE_RIG.md`) | Michael can rehearse and record a take — 🟡 built 2026-11-20; camera blocked, needs a real-playing check |
| **M2 palette live** | palette module in TD; pitch-class (chroma) analysis of the guitar; a root-coloured mode | playing a chord paints its root's colour |
| **M3 chart book + form clock** | load a chart in TD; count-off sets tempo; bar/section clock; one original made `playable` | the visual knows which bar and chord it's on |
| **M4 the circles** | three-circle notation drawn live from chart + audio | "playing duo" |

Delivery track (in parallel, later): a page on the Bandzoogle site for 8 Little Prayers with the
process story and a sign-up; short cuts for Reels; Claude can help in the browser when we get there.

## 5. Decisions and open questions

- 2026-11-20: solo guitar first; audio straight from the Focusrite (USB ASIO, inputs 1+2 by default). (Check: can Ableton and TD share the
  interface at the same time on Windows? Only if needed.)
- 2026-11-20: Michael's Gangster Flick illustration is kept out of this public repo (his artwork; colours there
  are layer colours, not synesthesia).
- Open: fixed vs relative do for harmony circles; colours for Cb/Fb/E#/B#; accent resolution (see NOTATION.md).

## 6. Session log

- **2026-11-20 — session 1.** Bootstrap (M0): palette, chart schema, Gangster Flick sketch, chartlib + tests,
  palette swatch render.
- **2026-11-20 — session 1b.** Local folder linked to GitHub. M1 skeleton built by `scripts/build_live.py`
  (logic in `modules/show/`): Focusrite USB ASIO inputs 1+2, C920 webcam (stuck "Initializing" - in use by
  another app or blocked by Windows camera privacy?), Rehearse/Record with countdown, Space/Esc/R/H, take
  naming, TDlive window. Test take OK (1280x720 60 fps MJPEG + stereo audio). Palette: Ab tuned redder.
