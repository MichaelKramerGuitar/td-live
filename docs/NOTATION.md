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

## Drawn live: the Notation mode

TDlive's **Notation (three circles)** mode draws all three circles from the chart, the song clock and the pitch
follower (`modules/notation/prims.py` -> `draw.frag`; parameters on `visuals/notation` › Notation):

- **Outer:** the meter polygon (flat top; beat 1 starts at the top-left corner and runs clockwise, so beats sit
  on corners and "ands" mid-side); accent balls from `rhythm.accents`; a light travels it with the beat.
- **Middle:** the circle of fifths with the current chord-scale's nodes (palette colours of their spelling);
  harmony circles at each chord's root, outside = major, inside = minor (by the chord's 3rd); inside each, the
  chord tones on a small circle of fifths (**fixed do** for now: C at the top) joined into a polygon. Current
  chord bright, next half-lit, the rest faint (toggle *Show The Tune's Harmonic Map*). Played notes flare on the
  ring and are joined in order.
- **Melodic nodes** (chart `melody`): a ring on the circle of fifths and a ring at that note inside the current
  harmony circle, so you see what it is over the chord; the caption names it (`F#  9 → 13`: the 9th of E-7
  becomes the 13th of A7). The next node shows as a faint ring.
- **Inner:** phrasing. The current phrase group's shape (sides = bars), gold spokes where its sub-groups begin,
  the bar being played filling in gold; small shapes below = the section's phrase groups; dots above = sections
  in play order. Sections without `phrasings` use shape × zig-zag as before.
- TDlive window, Notation row: **CAPTION**, **HARMONIC MAP** (all chords faint), **NOTE NAMES**, **HARMONY
  CIRCLES** fixed do / movable do (root at the top: same quality = same shape), **PHRASING** (1st / 2nd hearing
  / alternate every chorus).

## Phrasing and melodic nodes in the chart (schema 0.2 additions)

```yaml
form:
  sections:
    - name: A
      shape: 14
      phrasings: [[[2, 8], 4], [[8, 2], 4]]   # 10 + 4, the 10 heard as 2 + 8 or as 8 + 2 (first = default)
melody:                                      # degrees of the key (key-free, like the numerals)
  A: ["#3", "2", "5", null, ...]             # null = the previous node carries on
     # a bar can list one node per chord: ["7", "#2"]  (C over G-7b5, E over C7alt in Db)
```

A group is a number of bars or a list of sub-groups; groups must add up to the section's bars.

## Key-free charts (Roman numerals)

A chart with `changes_notation: roman` writes its changes relative to the key (`I7`, `ii-7`, `#IVo7`, `bVI7`),
always relative to the **major** scale (so in a minor key: `i-7`, `bIIImaj7`). The key is picked at
rehearsal/performance time (or `default_key`), and `tools/harmony.py` spells every chord and chord-scale in that
key with **letter arithmetic**: `bVI` in C is Ab (never G#), the seventh of a diminished chord is a double flat
when the harmony says so. Keys are offered as key signatures (C, G, D, A, E, B, F#, C#, F, Bb, Eb, Ab, Db, Gb,
Cb), so choosing Db rather than C# is a musical choice that also chooses the colours.

First key-free charts: `charts/blues_jazz.yaml` (12-bar jazz blues, default F),
`charts/rhythm_changes.yaml` (AABA, default Bb) and `charts/stablemates.yaml` (Golson, A1 14, B 8, A2 14 = 36 bars,
default Db, Michael's changes and melodic nodes; A1 turns into the bridge on C7alt, A2 ends on Dbmaj7). Stablemates' `E-7 A7` in Db is written `#ii-7 #V7`
(Michael spells E, not Fb), so in C it reads `D#-7 G#7`; a per-key respelling is an open question.

### Overrides and variants

- **Per-chord chord-scale:** `[VI7, 4, {scale: half_whole}]` instead of `[VI7, 4]`. Scales: ionian, lydian,
  mixolydian, dorian, aeolian, phrygian, locrian, melodic_minor, lydian_dominant, altered, diminished,
  half_whole. Defaults by quality: 7 -> mixolydian, -7 -> dorian, maj7/6 -> ionian, ø7 -> locrian,
  o7 -> diminished (whole-half), -6 -> melodic minor, 7alt -> altered.
- **Variants (inheritance):** `extends: blues_jazz` inherits a whole chart; any top-level field replaces the
  parent's, and `changes_patch: {chorus: {4: [[I7, 4]]}}` replaces single bars. Example:
  `charts/blues_basic.yaml` (the 3-chord blues in 7 lines).

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
