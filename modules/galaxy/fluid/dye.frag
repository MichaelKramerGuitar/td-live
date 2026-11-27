// Fluid: the ink. Advected by the flow, slowly fading; the traveller pours ink in the colour of what it's playing,
// a note adds a richer drop. in 0: dye (last frame, higher resolution)  in 1: velocity (sim grid)
//@COMMON
out vec4 fragColor;
void main()
{
    vec2 res = vec2(textureSize(sTD2DInputs[0], 0));
    vec2 uv = gl_FragCoord.xy / res;
    vec2 vres = vec2(textureSize(sTD2DInputs[1], 0));
    vec2 v = texture(sTD2DInputs[1], uv).xy / vres;      // cells/frame -> uv/frame
    vec3 d = texture(sTD2DInputs[0], uv - v).rgb * uDye.w;
    vec2 t = (uv - uTrav.xy) * vec2(uMisc.y, 1.0);
    float g = exp(-dot(t, t) / (uInj.z * uInj.z * 0.5));
    d += uDye.rgb * g * (uInj.y + 2.0 * uInj.w);
    // background ink: a faint, streaky supply along the edges that the flow carries in (grey or the harmony's shade)
    float edge = smoothstep(0.05, 0.0, min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y)));
    vec2 hd = (uv - uHome.xy) * vec2(uMisc.y, 1.0);
    float streak = 0.5 + 0.5 * sin(atan(hd.y, hd.x) * 23.0 + uMisc.z * 0.4) * sin(atan(hd.y, hd.x) * 7.0 - uMisc.z * 0.23);
    d += uBg.rgb * uBg.w * edge * streak;
    fragColor = vec4(d, 1.0);
}
