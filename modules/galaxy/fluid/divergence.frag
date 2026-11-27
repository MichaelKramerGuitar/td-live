// Fluid: divergence of the velocity. in 0: velocity
out vec4 fragColor;
void main()
{
    ivec2 p = ivec2(gl_FragCoord.xy);
    ivec2 r = textureSize(sTD2DInputs[0], 0);
    float uL = texelFetch(sTD2DInputs[0], clamp(p - ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float uR = texelFetch(sTD2DInputs[0], clamp(p + ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float vB = texelFetch(sTD2DInputs[0], clamp(p - ivec2(0, 1), ivec2(0), r - 1), 0).y;
    float vT = texelFetch(sTD2DInputs[0], clamp(p + ivec2(0, 1), ivec2(0), r - 1), 0).y;
    fragColor = vec4(0.5 * ((uR - uL) + (vT - vB)), 0.0, 0.0, 1.0);
}
