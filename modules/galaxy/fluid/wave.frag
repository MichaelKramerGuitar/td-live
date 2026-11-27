// Fluid: the bat's pings. A 2D wave equation (r = height now, g = height a frame ago) whose speed follows the
// depth of the creek bed (waves run faster in the valleys, slower over the shallows, as in shallow water:
// c ~ sqrt(depth)), so each ring shows the shape underneath as it travels. in 0: wave (last frame)  in 1: bed
//@COMMON
out vec4 fragColor;
void main()
{
    ivec2 p = ivec2(gl_FragCoord.xy);
    ivec2 r = textureSize(sTD2DInputs[0], 0);
    vec2 uv = (vec2(p) + 0.5) / vec2(r);
    vec2 w = texelFetch(sTD2DInputs[0], p, 0).xy;
    float L = texelFetch(sTD2DInputs[0], clamp(p - ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float R = texelFetch(sTD2DInputs[0], clamp(p + ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float B = texelFetch(sTD2DInputs[0], clamp(p - ivec2(0, 1), ivec2(0), r - 1), 0).x;
    float T = texelFetch(sTD2DInputs[0], clamp(p + ivec2(0, 1), ivec2(0), r - 1), 0).x;
    float h = texture(sTD2DInputs[1], uv).r;
    float depth = clamp(0.25 - h, 0.02, 1.0);
    float c2 = clamp(uBed.z * uBed.z * depth, 0.0, 0.45);
    float next = (2.0 * w.x - w.y + c2 * (L + R + B + T - 4.0 * w.x)) * 0.985;
    vec2 t = (uv - uTrav.xy) * vec2(uMisc.y, 1.0);
    next += uBed.w * exp(-dot(t, t) / 0.00015);
    fragColor = vec4(next, w.x, 0.0, 1.0);
}
