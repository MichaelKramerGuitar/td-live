// Fluid: one Jacobi iteration of the pressure solve. in 0: pressure  in 1: divergence
out vec4 fragColor;
void main()
{
    ivec2 p = ivec2(gl_FragCoord.xy);
    ivec2 r = textureSize(sTD2DInputs[0], 0);
    float L = texelFetch(sTD2DInputs[0], clamp(p - ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float R = texelFetch(sTD2DInputs[0], clamp(p + ivec2(1, 0), ivec2(0), r - 1), 0).x;
    float B = texelFetch(sTD2DInputs[0], clamp(p - ivec2(0, 1), ivec2(0), r - 1), 0).x;
    float T = texelFetch(sTD2DInputs[0], clamp(p + ivec2(0, 1), ivec2(0), r - 1), 0).x;
    float d = texelFetch(sTD2DInputs[1], p, 0).x;
    fragColor = vec4(0.25 * (L + R + B + T - d), 0.0, 0.0, 1.0);
}
