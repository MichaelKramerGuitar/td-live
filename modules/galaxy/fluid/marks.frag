// Fluid: the 12 key stars and the traveller as soft marks, top-down (added over the ink when SHOW = with stars).
// in 0: marks (row 0: u, v, size, alpha; row 1: r, g, b)
//@COMMON
out vec4 fragColor;
void main()
{
    vec2 uv = vUV.st;
    vec3 col = vec3(0.0);
    int nm = textureSize(sTD2DInputs[0], 0).x;
    vec2 a = vec2(uMisc.y, 1.0);
    for (int i = 0; i < nm; i++) {
        vec4 m = texelFetch(sTD2DInputs[0], ivec2(i, 0), 0);
        if (m.w <= 0.0) continue;
        vec3 mc = texelFetch(sTD2DInputs[0], ivec2(i, 1), 0).rgb;
        float d = length((uv - m.xy) * a);
        col += mc * m.w * (smoothstep(m.z, m.z * 0.6, d) * 0.8 + 0.35 * exp(-d / (m.z * 2.5)));
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
