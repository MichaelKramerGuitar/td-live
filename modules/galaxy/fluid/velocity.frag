// Fluid: velocity step = advect + forces + vorticity confinement + viscosity.
// in 0: velocity (last frame)  in 1: curl  in 2: bed (r = height of the harmony landscape)
// Forces: the background current (none / a whirl around home that also stirs the local key / a stream that turns
// with the form), the creek bed (water is pushed down the bed's slopes and dragged over the shallows), and the
// traveller pushing along its heading, plus a radial burst on each note.
//@COMMON
out vec4 fragColor;
vec2 V(vec2 c) { return texture(sTD2DInputs[0], c / vec2(textureSize(sTD2DInputs[0], 0))).xy; }
void main()
{
    vec2 res = vec2(textureSize(sTD2DInputs[0], 0));
    vec2 c = gl_FragCoord.xy;
    vec2 uv = c / res;
    // advect (semi-Lagrangian)
    vec2 v = V(c - V(c));
    // vorticity confinement: keeps the swirls alive
    ivec2 p = ivec2(c);
    float cL = abs(texelFetch(sTD2DInputs[1], p - ivec2(1, 0), 0).x);
    float cR = abs(texelFetch(sTD2DInputs[1], p + ivec2(1, 0), 0).x);
    float cB = abs(texelFetch(sTD2DInputs[1], p - ivec2(0, 1), 0).x);
    float cT = abs(texelFetch(sTD2DInputs[1], p + ivec2(0, 1), 0).x);
    float cc = texelFetch(sTD2DInputs[1], p, 0).x;
    vec2 N = vec2(cR - cL, cT - cB);
    N /= length(N) + 1e-5;
    v += uMisc.x * vec2(N.y, -N.x) * cc;
    // background current
    vec2 a = vec2(uMisc.y, 1.0);                         // uv -> square units
    if (uFlow.x > 0.5 && uFlow.x < 1.5) {                // pull home: a slow whirlpool around home, a smaller one at the local key
        vec2 d = (uv - uHome.xy) * a;
        float r = length(d) + 1e-4;
        v += uFlow.y * vec2(-d.y, d.x) / r * smoothstep(0.0, 0.08, r) * exp(-r * 1.5);
        vec2 e = (uv - uHome.zw) * a;
        float q = length(e) + 1e-4;
        v += 0.6 * uFlow.y * vec2(e.y, -e.x) / q * smoothstep(0.0, 0.04, q) * exp(-q * 6.0);
    } else if (uFlow.x > 1.5) {                          // the form: one stream, turning as the chorus goes round
        v += uFlow.y * 0.4 * vec2(cos(uFlow.z), sin(uFlow.z));
    }
    // the creek bed: downhill push, drag over the shallows
    vec2 bres = vec2(textureSize(sTD2DInputs[2], 0));
    vec2 bt = 1.0 / bres;
    float hL = texture(sTD2DInputs[2], uv - vec2(bt.x, 0)).r, hR = texture(sTD2DInputs[2], uv + vec2(bt.x, 0)).r;
    float hB = texture(sTD2DInputs[2], uv - vec2(0, bt.y)).r, hT = texture(sTD2DInputs[2], uv + vec2(0, bt.y)).r;
    float h = texture(sTD2DInputs[2], uv).r;
    v -= uBed.x * vec2(hR - hL, hT - hB) * 40.0;
    v *= 1.0 - uBed.y * smoothstep(-0.2, 0.2, h);
    // the traveller pushes along its heading; a note bursts outward
    vec2 t = (uv - uTrav.xy) * a;
    float g = exp(-dot(t, t) / (uInj.z * uInj.z));
    v += uInj.x * uTrav.zw * g;
    v += uInj.w * 3.0 * normalize(t + 1e-5) * g;
    // viscosity (simple damping) and a safety clamp
    v *= 1.0 - uFlow.w;
    float s = length(v);
    if (s > 6.0) v *= 6.0 / s;
    fragColor = vec4(v, 0.0, 1.0);
}
