// Harmony Galaxy, Attractor texture: particle colours (one pixel = one particle, same layout as the simulation).
// Home's particles in the home key's palette colour, travellers in the local key's; streaming ones a bit brighter.
uniform vec4 uHomeCol;    // rgb, w = brightness
uniform vec4 uLocalCol;   // rgb, w = share of particles at home
out vec4 fragColor;
void main()
{
    ivec2 ij = ivec2(gl_FragCoord.xy);
    ivec2 res = textureSize(sTD2DInputs[0], 0);
    float fi = float(ij.y * res.x + ij.x) / float(res.x * res.y);
    vec4 st = texelFetch(sTD2DInputs[0], ij, 0);
    bool home = fi < uLocalCol.w;
    vec3 c = home ? uHomeCol.rgb * 0.75 : uLocalCol.rgb;
    float b = uHomeCol.w * (st.w < -0.5 && !home ? 1.6 : 1.0);
    fragColor = vec4(c * b, 1.0);
}
