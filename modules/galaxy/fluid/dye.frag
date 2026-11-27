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
    fragColor = vec4(d, 1.0);
}
