// Fluid: what you see. Ink in water: the dye, refracted by the pings' ripples, tone-mapped so dense ink glows;
// faster water glints a little. (The key stars are drawn by marks.frag and added after.)
// in 0: dye  in 1: wave  in 2: velocity
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
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
