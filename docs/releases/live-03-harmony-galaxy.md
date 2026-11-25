# live-03 — Harmony Galaxy

The first Harmony Journey picture: harmony as a world you travel through, after Dan Tepfer's *Tonal Harmony in
3D* (blog post 2023-10-14 and video), shaped by Michael's own hearing of each tune.

## What's new

- **Harmony Galaxy mode.**
  - The 12 keys are stars in a gravity landscape. Home sits at the bottom of the deepest valley; keys are placed
    by their distance around the circle of fifths, so travelling further from home means climbing. Home's
    cohorts (minor-third: C Eb Gb A; major-third/Coltrane: C E Ab) dig their own, shallower valleys.
  - The local key (read from Michael's analysis in the chart) deepens its valley and carries its 7 diatonic
    chords as orbiting planets; secondary chords circle the chord they point at as moons.
  - A traveller moves from chord to chord with a trail; a tether home sags when slack and pulls taut and red as
    tension rises (four weighted dials: circle-of-fifths distance, torus distance, secondary depth, outside
    tones).
  - **Protagonist:** a comet, or the **melody whisp** — each note you play puffs out of the traveller in its
    palette colour, higher for higher notes, and is left behind as a glowing wake of your line.
  - **Camera:** body cam (riding with the traveller, looking where it's heading), follow, or from above.
  - Controls in the window's mode row: camera view, protagonist, gravity grid, tether, key names, caption.
- **The harmony model** (`tools/journey.py`): cohorts and the key torus (3 minor-third x 4 major-third cohorts),
  the perfect-cadence family (four dominants a minor third apart with their rootless dim7s, spelled toward the
  target), the minor-6 plagal family, related ii, secondary dominants and tritone subs, tension dials, and a
  reader for Michael's per-chord analysis.
- **New charts:** *All The Things You Are* and *Along Came Betty* (Michael's changes and his hearing of every
  chord), plus slash chords, -9, maj13 and 7b9.
- **Performance meter:** play any chart in 3/4 to 9/4 with groupings (7/4 as 4+3, 3+4 or 2+2+3); chords re-fit
  to the bar and accents move to the group starts. METER button in the window.
- **Endings, hands-free:** charts can have an ending for the last chorus; press **E** or **PageDown** (or a
  Bluetooth page-turner pedal) and the tune ends after this chorus, rings its last chord and stops by itself.
- The Notation mode shares its drawing shader with the Galaxy; the window's mode row now holds each mode's own
  controls.

## Sources

Dan Tepfer (*Tonal Harmony in 3D*), Barry Harris (dim7 as rootless dominant 7b9), Dmitri Tymoczko (*A Geometry
of Music*), the Tonnetz / neo-Riemannian theory, Allen Forte (*The Structure of Atonal Music*). Details in the
project's harmony-journey notes.

## Next

The same world with richer textures and physics: how the universe looks, and how we move through it.
