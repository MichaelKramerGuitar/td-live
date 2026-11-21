# The live rig (M1 skeleton)

## Using it

1. Open `TDlive.toe`: the **TDlive window opens by itself** after a moment. If you close it, select
   `/project1/show`, press **P** for its parameters and click **Open TDlive Window**.
2. Play and watch the green **input meter** above the buttons. Set `config` › Devices › **Input Gain** so normal
   playing sits around the middle and the hardest attacks don't turn it red.
3. **Rehearse**: countdown, then live, no file. **● Record**: countdown, then a take in `Takes/`.
   Click the same button again (it reads **Stop**) or press **Space** to stop.
4. **Space** starts whatever is armed (the hint in the top-left corner says which) and stops anything running.
   **R** arms Record, **H** arms reHearse, **Esc** stops. Keys work while a TouchDesigner window has focus;
   use the TDlive window, because in the network editor Space also plays/pauses the timeline.
5. The buttons, in two rows:
   - **Rehearse**, **● Record** (each becomes **Stop** while running), **Chart**, **Key**, **− bpm +**
     (2 bpm per click; click the number to go back to the chart's tempo).
   - **Mode**, **Me** (landscape: Outline / Ghost / Negative), **Cam** (you in or out of the shot), **16:9 / 9:16**,
     **Take** (cycles your takes, newest first; a new take is selected automatically), **▶ Play** / **■ Stop**.
   Chart, Key, Tempo, Format, Take and Play only work while idle.
   **Playback** shows the take in the TDlive window and sends its sound to the Focusrite; Space or Stop ends it,
   and starting a Rehearse/Record ends it too. The recorder never records playback.
   **Delete** (second row): click once (it reads **Delete?**), again within 4 s to delete the selected take. It
   disappears from the list at once; the file is removed as soon as Windows lets go of it (TD can keep a played
   movie open), at the latest at the next start (pending list: `Takes/_delete_pending.txt`).
   **Export** makes a playable copy of the selected take in `Exports/`: H.264 + AAC .mp4 upscaled to 1080p
   (1920x1080, or 1080x1920 for 9:16), ready for YouTube/Instagram, in the background. Needs ffmpeg once:
   `winget install Gyan.FFmpeg` in a terminal (or set `config` › Export › ffmpeg.exe). Takes are the staging
   area (Hap: perfect for recording, but most players can't open it); exports are what you keep and share.
7. **Me** (landscape) cycles Outline / Ghost / Negative behind the land, then a corner tile ↖ ↗ ↙ ↘ (your
   natural camera, like a speaker on a call). Tile size, look (natural or styled) and opacity: `visuals/landscape`
   › Me page.
8. **Find Guitar Input** (`config` › Devices): press it and play for 6 s; it listens to every input and sets
   Guitar Inputs to the one(s) carrying the guitar. Result in Input Info.
6. With a chart, the countdown is a **musical count-in**: one bar of beats at the tempo (`song` › Count-in Bars),
   ending on the downbeat of bar 1. The status line then shows chorus, bar and chord. Tempo: `song` › Tempo
   (each chart has a default).

The countdown and the status line appear **only in the preview**, never in a take.

### Click (never recorded)

`show` › Click page: **Click** = Off / Visual / Audio / Visual + Audio, **Click Volume**, **Open Click Window**.
Needs a chart (it follows the song's tempo, including the count-in).
- Visual: the *TDlive click* window (always on top; put it on another monitor) flashes every beat, warm on beat 1,
  with the beat number, bar and chord -> next chord; plus a small dot in the TDlive window preview.
- Audio: a short tick (higher on beat 1) to the Focusrite outputs (`click/to_interface`).
- Takes record only the guitar input (`sources/audio_out`) and `output/final`, so neither click can get into one.
- The tick is frame-timed (±8 ms at 60 fps): fine for keeping your place, not a studio metronome.

Takes are Motion-JPEG `.mov` at the output size and 60 fps with the guitar's audio, named
`Takes/<date>_<time>_<mode>_<format>.mov`. They're big; convert/upscale with ffmpeg as in td-experiment.

## How it's built

`scripts/build_live.py` builds everything (run it again any time; it's idempotent):

```
exec(open(project.folder + '/scripts/build_live.py', encoding='utf-8').read(), globals())
```

| COMP | Shortcut | What |
|---|---|---|
| `config` | `op.Config` | Format (Width/Height), FPS, Takes folder; Devices page: ASIO device, guitar inputs (`1 2`), Input Gain, camera; Guitar page: Tuning (`standard`, `DADGCF`, `drop_D`, `DADGAD`, or notes low to high like `D A D G B E`) |
| `sources` | `op.Sources` | `audio_in` (Focusrite USB ASIO) → `guitar` (inputs averaged, mono) and `audio_out` (for takes); `camera` → `cam` (fitted to the format; black when the camera is off/missing) |
| `analysis` | `op.Analysis` | **the bus**, `analysis/out` |
| `visuals` | `op.Visuals` | one COMP per mode, each with `out1`: `mirror`, `ripples` |
| `visuals/landscape` | | Michael's fretboard landscape (built by `scripts/build_landscape.py`, shaders in `modules/landscape/`): `song/positions` -> `masses` / `mass_colors` (Script TOPs) -> `field` (GLSL: well depth + colour) -> `smooth` (eases between chords) -> line grids `terrain` / `frets` / `strings` (GLSL MAT sinks them into the wells) + `planets` (instanced, root/3rd/7th) -> `render` -> glow. Parameters: Flip (low string on the right), Depth, Spread, Contrast, Ease (chord morph speed), Brightness, Planet Size, Planets From Weight, Planet Clarity (radiant cloud .. crisp), Planet Radiance (halo); Me page (the camera as light behind the land): Style (ghost / outline / negative), Brightness, Follows Playing, Fade After Playing, Tint With Chord Root Colour, Cut The Room, Focus; Camera page: Eye Height, Eye Behind Bridge, Look Point, Field Of View |
| `output` | `op.Output` | `modes` switch → `final` (exactly what is recorded) → `recorder`; `preview` = final + countdown/status |
| `song` | `op.Song` | Chart / Key / Tempo / Count-in Bars / Frets; `engine` (form clock + harmony, from `tools/`); outputs `now` (where we are), `tones` (current chord-scale: note, interval, role, weight, colour), `positions` (every fretboard position of it, for the current Config › Guitar › Tuning), `out` CHOP (playing, counting_in, beat, bar, chorus, beat_phase, bar_phase, chord_index) |
| `show` | `op.Show` | Rehearse / Record / Stop / Armed / Mode / Me In Shot / Countdown / Status; the TDlive window (`panel`, `window`); keys |

### The bus contract (`op.Analysis.op('out')`, all 0..1)

| Channel | Meaning |
|---|---|
| `level` | overall loudness (RMS × Input Gain), quick attack, ~0.25 s release |
| `hit` | attack envelope: jumps to 1 when the level leaps above its own recent average, decays in ~0.35 s |
| `low` / `mid` / `high` | loudness below 250 Hz / around 1 kHz / above 3 kHz |

A mode may read the bus, `op.Sources.op('cam')` and `op.Config`, and nothing else. That's what keeps modes
swappable (same idea as td-experiment's bus). M2 adds pitch channels (chroma) here.

### Logic you can edit (`modules/show/`)

| File | DAT | Does |
|---|---|---|
| `logic.py` | `show/logic` | the state machine: idle → countdown → running; names takes; overlay text; Status |
| `actions.py` | `show/actions` | parameter pulses → logic |
| `tick.py` | `show/tick` | once per frame → `logic.tick()` |
| `keys.py` | `show/keys` | Space / Esc / R / H → logic |
| `buttons.py` | `show/buttons` | TDlive window buttons → logic |

These DATs are synced to the files: edit in VS Code and TouchDesigner re-reads them. `modules/song/` works the
same way (`engine.py`, `setup.py`, `params.py`); the music theory itself lives in `tools/` (harmony, formclock,
chartlib) so it can be tested without TouchDesigner (`python -m pytest tests`). After editing a file in
`tools/`, restart TD (Python keeps the old module loaded).

### Camera notes

- The Logitech C920 runs at **640x480** for now. Its HD modes (1280x720 / 1920x1080 at 30 fps) stall at
  "Initializing..." in this TD build, and switching back to 640x480 brings it back. 640x480 is soft in 16:9 and
  quite soft in 9:16 (it's cropped). To try later: Media Foundation driver, other USB port (not a hub), or
  OBS as the capture app feeding TD.
- If the camera ever sticks at "Initializing...", set Signal Format back to 640x480, or delete `sources/camera`,
  add a fresh Video Device In TOP named `camera` by hand, pick the C920 and connect it to `camera_or_black`.

### Landscape gotchas (TD 2025)

- GLSL TOPs premultiply RGB by alpha by default. For data textures (positions, heights) turn
  `Premultiply RGB by Alpha` off, or x/y/z get multiplied by the alpha channel.
- A Sphere SOP with Type = Polygon plus custom rows/cols drew nothing when instanced; the default sphere works.
- TOP to CHOP converts colour space (sRGB) by default; for data set Output Color Space to `passthrough`.
- An instancing Geometry COMP that got into a bad state stayed broken; the build always makes it fresh.

### Timeline gotcha

- Execute DAT frame callbacks and TD's `run(delayFrames=...)` only advance while the TIMELINE plays, and Space in
  the network editor pauses it - which froze the show (a take never started). The rig now keeps the timeline
  playing: a watchdog on the real clock (`run(delayMilliSeconds=...)`, which keeps going while paused) resumes it
  within 250 ms, and Space also resumes it straight away.

### Takes gotchas

- TD can keep a played movie open after playback (even with the File cleared), and Windows refuses to delete an
  open file. Delete therefore hides the take at once and retries the file every ~2 s and at the next start.
- Audio File Out / Audio File In on takes: not used. Audio File Out only writes when something pulls on it,
  and stopping an Audio File In that reads a .mov while clearing its file froze TD. Playback sound comes from an
  Audio Movie CHOP following the movie player.
- Recording: MJPEG costs ~20 fps here (34 -> 15); Hap costs ~2. Takes stay in sync either way (TD repeats
  frames to keep real time).

### Gotchas carried over from td-experiment

- The recorder opens its file the moment `record` turns on, so `logic._record` sets the name first and starts a
  frame later.
- Don't save the project mid-take: a `.toe` saved while recording reopens recording.
- Save with **Ctrl+S** yourself (`project.save()` through the bridge has hung TD).

## Exercise (Michael)

Add a third mode by hand: copy `visuals/ripples` to `visuals/<name>`, change one thing, then add it to
`MODES` in `build_live.py` and re-run the build. You'll touch the whole contract (bus in, `out1` out, mode menu)
in five minutes.
