# live-02 — Three Circles

TDlive learns to draw Michael's own chart notation live, prototyped on Benny Golson's *Stablemates*, and the
rig gets a cleaner, more playable window.

## What's new

- **Notation mode (three circles)** — Mode › *Notation*. Michael's notation as a living picture of the tune:
  - *Outer — rhythm:* a polygon with one side per beat (a square in 4/4); balls on it are the chart's accents;
    a light travels the perimeter with the beat, and an accent flares as it passes.
  - *Middle — pitch:* the circle of fifths, C at the top. Each of its 12 nodes takes the palette colour of its
    spelling, larger for the notes of the current chord-scale. Every chord of the tune sits on it as a
    harmony circle at its root — outside for major, inside for minor — and each harmony circle is itself a
    little circle of fifths whose polygon joins the chord tones, so its shape *is* the chord's interval
    structure. The current chord glows, the next is half-lit, the rest of the tune stays as a faint harmonic
    map. Notes Michael plays flare on the ring and are joined in order: the line as a constellation in
    fifths-space.
  - *Inner — form:* the current section's shape (sides = bars), its zig-zag multiplier and repeat hashes, the
    bar being played filling in gold; dots underneath show the sections in play order.
- **Stablemates** — Michael's changes and melodic nodes (A1 14, B 8, A2 14), stored key-free, spelled exactly as
  he writes it in Db; phrased 10 + 4, the 10 heard as 2 + 8 or 8 + 2.
- **Melodic nodes and phrasing in the chart format** — melody notes per bar as key-free degrees, named live
  over each chord (`F#  9 → 13`); alternative phrasings per section.
- **Notation row** in the window: Caption, Harmonic map, Note names, Fixed / Movable do, Phrasing
  (1st / 2nd / alternate every chorus).
- **A new TDlive window** — header status line (out of the picture), captioned controls, buttons sized to their
  text, grouped rows, colours for armed / recording / rehearsing / playing / exporting.
- **Click buttons** — Visual (opens/closes its window) and Audio, and *Every*: beat, bar, or **form** (section
  tops + a count into each new section, bar-in-section on the big number).
- **Export progress** — percentage, progress bar and time left while ffmpeg works.
- **Gesture whisp** in the landscape (already in live-01's tag commit) and the pitch follower behind it.

## Notes

- Next: the palette pass (Michael hones the colours by eye).
