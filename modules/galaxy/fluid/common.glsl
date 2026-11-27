// Harmony Galaxy, Fluid texture: shared uniforms (each pass declares this block; Python sets them every frame).
// Velocity is in grid cells per frame; the grid lies flat on the galaxy plane (top-down, +z up the screen).
uniform vec4 uTrav;   // xy traveller (uv), zw heading (unit, cells)
uniform vec4 uInj;    // x push, y dye amount, z radius (uv), w note pulse this frame (0/1)
uniform vec4 uDye;    // rgb dye colour, w dye decay per frame
uniform vec4 uFlow;   // x current mode (0 none, 1 pull home, 2 the form), y strength, z form angle, w viscosity
uniform vec4 uHome;   // xy home (uv), zw local key (uv)
uniform vec4 uBed;    // x bed slope force, y drag over shallows, z wave speed, w ping amplitude (0 = no ping)
uniform vec4 uMisc;   // x vorticity confinement, y aspect (w/h), z time, w ink brightness
