// Planet instance transforms (GLSL TOP), one pixel per mass: (x, height, z, radius) in world units.
// Inputs: 0 = masses, 1 = the smoothed field (so planets sit in their wells as the surface morphs).
uniform vec4 uY;       // ymin, ymax, planet min weight (lighter masses stay dents)
uniform vec4 uWorld;   // string spacing, neck length, well depth, planet size
out vec4 fragColor;
void main()
{
    vec4 m = texelFetch(sTD2DInputs[0], ivec2(gl_FragCoord.xy), 0);
    float ymax = uY.y;
    vec2 tc = vec2((m.x + 0.5) / 6.0, (m.y - uY.x) / (uY.y - uY.x));
    float h = texture(sTD2DInputs[1], tc).a;
    float r = (m.w > 0.5 && m.z >= uY.z) ? uWorld.w * (0.35 + 0.65 * m.z) : 0.0;
    fragColor = TDOutputSwizzle(vec4((m.x - 2.5) * uWorld.x, -h * uWorld.z + r * 0.6, -(ymax - m.y) * uWorld.y, r));
}
