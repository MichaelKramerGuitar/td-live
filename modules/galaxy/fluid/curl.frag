// Fluid: curl (vorticity) of the velocity. in 0: velocity
out vec4 fragColor;
void main()
{
    ivec2 p = ivec2(gl_FragCoord.xy);
    float vL = texelFetch(sTD2DInputs[0], p - ivec2(1, 0), 0).y;
    float vR = texelFetch(sTD2DInputs[0], p + ivec2(1, 0), 0).y;
    float uB = texelFetch(sTD2DInputs[0], p - ivec2(0, 1), 0).x;
    float uT = texelFetch(sTD2DInputs[0], p + ivec2(0, 1), 0).x;
    fragColor = vec4(0.5 * ((vR - vL) - (uT - uB)), 0.0, 0.0, 1.0);
}
