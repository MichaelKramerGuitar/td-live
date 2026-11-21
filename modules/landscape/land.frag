// Fretboard landscape (GLSL MAT, pixel): dim slate lines, coloured and brighter in the wells,
// fading toward the horizon (the nut). Audio: level adds glow, hits flash the wells.
uniform vec4 uLook;    // brightness, level, hit, opacity
uniform vec3 uBase;    // line colour outside the wells
in Vertex { vec3 color; float depth; float h; } iVert;
out vec4 fragColor;
void main()
{
    TDCheckDiscard();
    float inf = clamp(iVert.h * 1.4, 0.0, 1.0);
    vec3 c = mix(uBase, iVert.color, inf);
    float fog = 1.0 - smoothstep(0.35, 1.0, iVert.depth);
    float b = uLook.x * (0.55 + 0.9 * inf) * (1.0 + 0.8 * uLook.y) + 1.2 * uLook.z * inf;
    vec4 color = vec4(c * b * fog, uLook.w * fog);
    TDAlphaTest(color.a);
    fragColor = TDOutputSwizzle(color);
}
