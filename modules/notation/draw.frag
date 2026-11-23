// Three-circle notation (GLSL TOP). Draws every primitive from input 0 with soft anti-aliased edges + glow.
// Input 0: primitives, one column each, 3 rows:
//   row 0: type, ax, ay, bx     type 0 = line a->b, 1 = ring (centre a, radius bx), 2 = disc (centre a, radius bx),
//                               < 0 = end of list
//   row 1: by, half width, glow, alpha
//   row 2: r, g, b, -
// Coordinates: the short side of the frame spans -1..1 (the figure is drawn inside the unit circle).
uniform vec4 uLook;   // x = brightness, y = glow amount, z = glow reach, w = pixel size in figure units
out vec4 fragColor;

float segDist(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-8), 0.0, 1.0);
    return length(pa - ba * h);
}

void main()
{
    vec2 res = uTDOutputInfo.res.zw;
    vec2 p = (vUV.st - 0.5) * 2.0 * res / min(res.x, res.y);
    int n = textureSize(sTD2DInputs[0], 0).x;
    vec3 col = vec3(0.0);
    float px = uLook.w;
    for (int i = 0; i < n; i++) {
        vec4 r0 = texelFetch(sTD2DInputs[0], ivec2(i, 0), 0);
        if (r0.x < -0.5) break;
        vec4 r1 = texelFetch(sTD2DInputs[0], ivec2(i, 1), 0);
        vec4 r2 = texelFetch(sTD2DInputs[0], ivec2(i, 2), 0);
        float d;
        if (r0.x < 0.5)      d = segDist(p, r0.yz, vec2(r0.w, r1.x)) - r1.y;
        else if (r0.x < 1.5) d = abs(length(p - r0.yz) - r0.w) - r1.y;
        else                 d = length(p - r0.yz) - r0.w;
        float core = 1.0 - smoothstep(-px, px, d);
        float glow = r1.z * uLook.y * exp(-max(d, 0.0) / uLook.z);
        col += r2.rgb * r1.w * (core + glow);
    }
    col = 1.0 - exp(-col * uLook.x);          // soft tone map: overlaps bloom instead of clipping
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
