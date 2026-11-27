# live-05 — Fluid

Harmony Galaxy gets a third texture: ink in water. The harmony shapes the water (its depth, its current, its
drain), and your playing stirs it, drops ink into it and sends out pings. Michael, after playing it: "BY FAR the
most interactive feeling duo partner."

## What's new

- **Fluid texture** (Harmony Galaxy › TEXTURE = Fluid), seen flat from above.
  - Real-time fluid simulation on the graphics card: velocity, swirl (vorticity), pressure, ink.
  - **The creek bed** (Michael's first image: the bat over the mountains / water over a creek bed): the galaxy's
    wells become the bed under the water; shallows drag the flow.
  - **The traveller** (comet or melody whisp) pushes the water; each note onset drops a burst of ink in your
    synesthesia colours.
  - **Pings** (echolocation): rings that travel faster over deep water and slower over the shallows, so they map
    the harmony bed. On every note, on long notes only, or off.
  - **Current:** none, pull home, or follow the form.
  - **Drain:** with Pull home, water enters along the edges and drains into home's whirlpool.
  - **Background ink:** off, grey, or a muted, slowly shifting shade of the current chord's root colour, drawn in
    from the edges toward the whirlpool.
  - Settings on visuals/galaxy › Fluid (resolution, viscosity, swirl, push, ink amount and fade, bed, pings,
    wave speed, drain, background ink).
- **Beatrice** (Sam Rivers): 16 bars, from Michael's changes, melodic nodes and hearing.
- **Gestural function:** `journey.gestural()` recognises function carried by root motion alone: subV (down a
  half step), V (down a fifth), or a stepwise line of one quality; "softened" when the chord isn't a dominant 7
  (Dameron's Lady Bird turnaround, Beatrice's Gbmaj7#11 → Fmaj7).
- New chord quality: maj7#11.

## Performance

~30 fps with the fluid on; the fluid itself ~2 ms of GPU per frame.

## Sources

Stable fluids after Jos Stam, "Stable Fluids" (SIGGRAPH 1999), with vorticity confinement after Fedkiw, Stam &
Jensen (2001); implemented from the papers. Harmonic world after Dan Tepfer, *Tonal Harmony in 3D*. Images and
ideas: Michael's.

## Next

Image 2: harmony as the medium itself (thickness, pressure, air pockets), with the melody pushing against it.
