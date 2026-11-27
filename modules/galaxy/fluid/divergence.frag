// Fluid: divergence of the velocity, plus the drain: water is allowed to enter all along the edges and leave
// at home's whirlpool, so the pressure solve makes a flow that converges on it. in 0: velocity
//@COMMON
out vec4 fragColor;
void main()
{
    ivec2 p = ivec2(gl_FragCoord.xy);
    ivec2 r = textureSize(sTD2DInputs[0], 0);
    float uL = texelFetch(sTD2DInputs[0], clamp(p - ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float uR = texelFetch(sTD2DInputs[0], clamp(p + ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float vB = texelFetch(sTD2DInputs[0], clamp(p - ivec2(0, 1), ivec2(0), r - 1), 0).y;
    float vT = texelFetch(sTD2DInputs[0], clamp(p + ivec2(0, 1), ivec2(0), r - 1), 0).y;
    float div = 0.5 * ((uR - uL) + (vT - vB));
    // the drain: we want the flow to have divergence s = (sources along the edges) - (sink at home), with equal
    // totals Q (in cell areas per frame). The pressure solve then removes (div - s) instead of div.
    vec2 uv = (vec2(p) + 0.5) / vec2(r);
    float N = float(r.x * r.y);
    vec2 d = (uv - uHome.xy) * vec2(uMisc.y, 1.0);
    float sink = exp(-dot(d, d) / 0.002) / (3.14159 * 0.002 * N / uMisc.y);
    float edge = smoothstep(0.03, 0.0, min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y))) / (0.06 * N);
    float Q = uSink.x * 20.0;
    div -= Q * (edge - sink);
    fragColor = vec4(div, 0.0, 0.0, 1.0);
}
