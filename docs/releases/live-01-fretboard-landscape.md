# live-01 — Fretboard Landscape

The first state of TDlive that's ready for real takes: a live solo-guitar rig in TouchDesigner whose main visual
is Michael's own mental image of the fretboard.

## What it is

A huge fretboard trails off to the horizon in one-point perspective, seen from the bridge toward the nut. The
harmony of the moment sits on it like planetary bodies: every position of the current chord-scale bends the
surface, deeper for the notes that ground the harmony (root, then 3rd and 7th, then 5th, then tensions), coloured
by Michael's pitch–colour synesthesia. As the tune moves through its form, the land eases from one chord into
the next. Michael appears in a corner tile (or as light behind the land), and the whole picture breathes with
the energy of his playing.

## What's in it

- **Charts that know the tune** — Blues (jazz), Blues (basic, a variant of the jazz blues), Rhythm Changes,
  written key-free in Roman numerals and spelled in any of 15 keys by letter arithmetic (bVI in C is Ab, never
  G#), because the colours follow spelling. Per-chord scale overrides and chart inheritance.
- **Form clock** — pick chart, key and tempo; a one-bar musical count-in lands on bar 1; the rig follows chorus,
  bar and chord.
- **Fretboard landscape** — real fret spacing, configurable tuning (standard default), planets with adjustable
  clarity and radiance, chord morphing, glow with the playing.
- **Me** — outline / ghost / negative light behind the land, or a corner tile in the outline look.
- **Takes** — Rehearse or Record with count-in and Space bar; Hap recording at a steady 30 fps; playback with
  sound; Delete; Export to a 1080p H.264 .mp4 for YouTube/Instagram (needs ffmpeg).
- **Click** — visual (its own window + preview dot) and/or audio; never recorded.
- **Palette** — Michael's 17 spelled-pitch colours, in his own words, starting colours tuned by eye.

## Notes

- Built with Claude through the TouchDesigner MCP bridge; logic lives in repo files (`modules/`, `tools/`) and
  `scripts/build_live.py` rebuilds the whole network.
- Lessons on the way (TD 2025): data textures must not be premultiplied; Execute DAT frame callbacks stop when the
  timeline is paused (Space in the editor), so a real-clock watchdog keeps it playing; selecting audio inputs by
  index picked the wrong input here, so inputs are picked by name.

Next: melodic gestures over the fretboard, then fuller listening (played notes as masses).
