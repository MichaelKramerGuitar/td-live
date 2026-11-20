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
5. **Mode** cycles the visual modes, **Camera** puts you in or out of the shot, **Format** switches 16:9 / 9:16
   (only while idle, so a take never changes size).

The countdown and the status line appear **only in the preview**, never in a take.

Takes are Motion-JPEG `.mov` at the output size and 60 fps with the guitar's audio, named
`Takes/<date>_<time>_<mode>_<format>.mov`. They're big; convert/upscale with ffmpeg as in td-experiment.

## How it's built

`scripts/build_live.py` builds everything (run it again any time; it's idempotent):

```
exec(open(project.folder + '/scripts/build_live.py', encoding='utf-8').read(), globals())
```

| COMP | Shortcut | What |
|---|---|---|
| `config` | `op.Config` | Format (Width/Height), FPS, Takes folder; Devices page: ASIO device, guitar inputs (`1 2`), Input Gain, camera |
| `sources` | `op.Sources` | `audio_in` (Focusrite USB ASIO) → `guitar` (inputs averaged, mono) and `audio_out` (for takes); `camera` → `cam` (fitted to the format; black when the camera is off/missing) |
| `analysis` | `op.Analysis` | **the bus**, `analysis/out` |
| `visuals` | `op.Visuals` | one COMP per mode, each with `out1`: `mirror`, `ripples` |
| `output` | `op.Output` | `modes` switch → `final` (exactly what is recorded) → `recorder`; `preview` = final + countdown/status |
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

These DATs are synced to the files: edit in VS Code and TouchDesigner re-reads them.

### Camera notes

- The Logitech C920 runs at **640x480** for now. Its HD modes (1280x720 / 1920x1080 at 30 fps) stall at
  "Initializing..." in this TD build, and switching back to 640x480 brings it back. 640x480 is soft in 16:9 and
  quite soft in 9:16 (it's cropped). To try later: Media Foundation driver, other USB port (not a hub), or
  OBS as the capture app feeding TD.
- If the camera ever sticks at "Initializing...", set Signal Format back to 640x480, or delete `sources/camera`,
  add a fresh Video Device In TOP named `camera` by hand, pick the C920 and connect it to `camera_or_black`.

### Gotchas carried over from td-experiment

- The recorder opens its file the moment `record` turns on, so `logic._record` sets the name first and starts a
  frame later.
- Don't save the project mid-take: a `.toe` saved while recording reopens recording.
- Save with **Ctrl+S** yourself (`project.save()` through the bridge has hung TD).

## Exercise (Michael)

Add a third mode by hand: copy `visuals/ripples` to `visuals/<name>`, change one thing, then add it to
`MODES` in `build_live.py` and re-run the build. You'll touch the whole contract (bus in, `out1` out, mode menu)
in five minutes.
