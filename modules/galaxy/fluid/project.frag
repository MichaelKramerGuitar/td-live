// Fluid: subtract the pressure gradient (makes the flow incompressible: swirls instead of sinks).
// in 0: velocity  in 1: pressure
out vec4 fragColor;
void main()
{
    ivec2 p = ivec2(gl_FragCoord.xy);
    ivec2 r = textureSize(sTD2DInputs[1], 0);
    float L = texelFetch(sTD2DInputs[1], clamp(p - ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float R = texelFetch(sTD2DInputs[1], clamp(p + ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float B = texelFetch(sTD2DInputs[1], clamp(p - ivec2(0, 1), ivec2(0), r - 1), 0).x;
    float T = texelFetch(sTD2DInputs[1], clamp(p + ivec2(0, 1), ivec2(0), r - 1), 0).x;
    vec2 v = texelFetch(sTD2DInputs[0], p, 0).xy - 0.5 * vec2(R - L, T - B);
    // walls: no flow through the edges
    if (p.x == 0 || p.x == r.x - 1) v.x = 0.0;
    if (p.y == 0 || p.y == r.y - 1) v.y = 0.0;
    fragColor = vec4(v, 0.0, 1.0);
}
