// Fluid: what you see. Ink in water: the dye, refracted by the pings' ripples, tone-mapped so dense ink glows;
// faster water glints a little. With the stars: the 12 keys and the traveller as soft marks (in 3: marks).
// in 0: dye  in 1: wave  in 2: velocity  in 3: marks (row 0: u, v, size, alpha; row 1: r, g, b)
//@COMMON
out vec4 fragColor;
void main()
{
    vec2 uv = vUV.st;
    vec2 wt = 1.0 / vec2(textureSize(sTD2DInputs[1], 0));
    float wL = texture(sTD2DInputs[1], uv - vec2(wt.x, 0)).r, wR = texture(sTD2DInputs[1], uv + vec2(wt.x, 0)).r;
    float wB = texture(sTD2DInputs[1], uv - vec2(0, wt.y)).r, wT = texture(sTD2DInputs[1], uv + vec2(0, wt.y)).r;
    vec2 n = vec2(wR - wL, wT - wB);
    vec3 ink = texture(sTD2DInputs[0], uv + n * 0.02).rgb;
    float speed = length(texture(sTD2DInputs[2], uv).xy);
    vec3 col = 1.0 - exp(-ink * uMisc.w);
    col += vec3(0.6, 0.7, 0.9) * (0.15 * smoothstep(0.5, 3.0, speed) + 2.5 * max(0.0, n.x + n.y)) * 0.25;
    int nm = textureSize(sTD2DInputs[3], 0).x;
    vec2 a = vec2(uMisc.y, 1.0);
    for (int i = 0; i < nm; i++) {
        vec4 m = texelFetch(sTD2DInputs[3], ivec2(i, 0), 0);
        if (m.w <= 0.0) continue;
        vec3 mc = texelFetch(sTD2DInputs[3], ivec2(i, 1), 0).rgb;
        float d = length((uv - m.xy) * a);
        col += mc * m.w * (smoothstep(m.z, m.z * 0.6, d) * 0.8 + 0.35 * exp(-d / (m.z * 2.5)));
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
