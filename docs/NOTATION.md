# Three-circle notation → data

Michael's notation puts most of what you need to know about a tune into **one image you can take in at once**: a
memory aid, and a way of thinking about form and composition. TDlive stores the same information as a chart file
(`charts/<tune>.yaml`, schema `charts/schema/chart.schema.json`) so the visuals can know the tune too.

| Circle | Role | In the drawing | In the chart file |
|---|---|---|---|
| **Outer** | rhythm: pulse, feel, emphases | A polygon with one side per beat (pentagon = 5/4). Nodes ("balls") on it mark accents, syncopations, hemiolas. | `rhythm.meter`, `rhythm.accents` (1-based beats; `2.5` = the "and" of 2), `rhythm.feel` |
| **Middle** | pitch: melodic nodes, harmonic areas | The circle of fifths, C at the top. Small nodes = important melody notes. Harmony circles: **inside = minor, outside = major**; each is itself a circle of fifths whose polygon shows the chord's interval structure. | `pitch.melodic_nodes`, `pitch.harmonies` (`root`, `quality`, `tones`) |
| **Inner** | form: groupings of bars | A shape per section, sides = bars (square = 4, octagon = 8). A zig-zag inside **multiplies** it (square with a ×3 zig-zag = 12 bars, so no dodecagons). Hash marks = repeats. | `form.sections` (`shape`, `multiplier`, `hashes`) → bars = shape × multiplier, played hashes + 1 times |

The live system also needs to know **which chord is sounding in which bar**: that's `changes`, the one part that
isn't in the drawing. A chart without it is a `sketch`; with it, it's `playable`.

## Key-free charts (Roman numerals)

A chart with `changes_notation: roman` writes its changes relative to the key (`I7`, `ii-7`, `#IVo7`, `bVI7`),
always relative to the **major** scale (so in a minor key: `i-7`, `bIIImaj7`). The key is picked at
rehearsal/performance time (or `default_key`), and `tools/harmony.py` spells every chord and chord-scale in that
key with **letter arithmetic**: `bVI` in C is Ab (never G#), the seventh of a diminished chord is a double flat
when the harmony says so. Keys are offered as key signatures (C, G, D, A, E, B, F#, C#, F, Bb, Eb, Ab, Db, Gb,
Cb), so choosing Db rather than C# is a musical choice that also chooses the colours.

First key-free charts: `charts/blues_jazz.yaml` (12-bar jazz blues, default F) and
`charts/rhythm_changes.yaml` (AABA, default Bb).

## Why spelling is stored

Chord roots and melodic nodes are stored **spelled** (`Db`, not `C#` or a number). The palette
(`synesthesia/palette.yaml`) gives enharmonic spellings different colours, and audio can't tell them apart, so
the spelling has to come from the chart. The pitch tracker says *what sounds*; the chart says *what it's called*;
together they choose the colour.

## Example: Gangster Flick

`charts/gangster_flick.yaml` — 5/4; melodic nodes C, G, F#/Gb, Ab, Db; three minor and three major harmony
circles (roots still to fill in); form A = 8 bars × 4, B = 12 bars, C = 20 bars × 2 → **84 bars**.

## Open questions (decide when they matter)

- Harmony circles: "fixed do" or "relative do"? (Michael has gone back and forth.) The data stores spelled chord
  tones, which works either way; it only affects how a harmony circle is *drawn*.
- Accents finer than an eighth note: keep fractional beats, or switch to a subdivision grid (e.g. 16ths)?
- `F#/Gb`-style undecided spellings: fine for a sketch; a playable chart should pick one per bar.

## Tools

```
python tools/check_book.py        # validate every chart + the palette, print each chart's form
python tools/render_palette.py    # docs/img/palette.png: starting colours on the circle of fifths
python tools/render_fretboard.py F I7 '#IVo7' ii-7   # docs/img/fretboard_F.png: chord-scales on the neck
python -m pytest tests            # the musical rules (spelling, circle of fifths, form arithmetic)
```
