# live-04 — Attractors

Same world, new texture: Harmony Galaxy's harmonic gravity drawn as strange attractors. Each key area holds its
own chaotic system, and the music's journey streams tens of thousands of particles from one to the next.

## What's new

- **Attractor texture** (Harmony Galaxy › TEXTURE = Attractor).
  - 32,000 particles simulated on the graphics card every frame.
  - **One attractor per kind of key:** home = Aizawa; the Coltrane (major-third) cohort = Halvorsen (alternative:
    Three-Scroll Unified Chaotic System); the minor-third cohort = Four-Wing; keys one or two steps round the
    circle of fifths = Thomas; keys further out = Lorenz.
  - **Tension sets how wild it gets:** near home a quiet, laminar orbit (settled but alive); as the tension dials
    rise the orbit frays into the full strange attractor. Lorenz is calm or fully wild, nothing in between.
  - **The journey:** when the local key changes, the travelling particles let go, stream toward the new key with
    a little swirl, and dissolve onto its attractor. A quarter of the particles always stay on home's orbit: the
    memory of home.
  - **Particles as** points, trails, or both; **show** with the stars and planets, or abstract.
  - Works with every camera (body cam rides inside the flow) and with the melody whisp.
  - Window controls: TEXTURE, PARTICLES, SHOW. Settings on visuals/galaxy › Attractor.
- **Offline prototype tools:** `tools/attractors.py` (the seven attractors, normalised, with the tension blend
  and the role mapping) and `scripts/proto_attractors.py` (contact sheets); `scripts/gen_attractor_glsl.py`
  generates the GPU simulation from the same Python, so prototype and live rig share their numbers.

## Performance

Simulation ~0.1 ms per frame; drawing 1-7 ms; ~28 fps in body cam with everything on.

## Sources

Attractor equations and parameter values as listed by Juan Carlos Ponce Campuzano, *Strange Attractors*
(dynamicmath.xyz/strange-attractors), implemented from the maths (no code copied): Lorenz (1963), Thomas
(1999), Langford/Aizawa, Dadras & Momeni (2009), Halvorsen (via Sprott, *Elegant Chaos*), the Three-Scroll
Unified Chaotic System, the Four-Wing system. Harmonic world after Dan Tepfer, *Tonal Harmony in 3D*.

## Next

Fluid: velocity, pressure, density and temperature mapped onto the same world.
