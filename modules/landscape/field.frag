// Landscape height + colour field (GLSL TOP). x = across the strings, y = along the neck (nut .. bridge).
// Inputs: 0 = masses (string, y, weight, valid), 1 = mass colours (r, g, b, weight).
// Out: rgb = palette colour of the nearest masses (weighted), a = depth of the well (sum of gaussians).
uniform vec4 uY;      // ymin, ymax, sigma across (strings), sigma along (scale-length fraction)
out vec4 fragColor;
void main()
{
    float s = vUV.s * 6.0 - 0.5;
    float y = mix(uY.x, uY.y, vUV.t);
    int n = textureSize(sTD2DInputs[0], 0).x;
    float h = 0.0, wsum = 0.0;
    vec3 col = vec3(0.0);
    for (int i = 0; i < n; i++) {
        vec4 m = texelFetch(sTD2DInputs[0], ivec2(i, 0), 0);
        if (m.w < 0.5) continue;
        vec4 c = texelFetch(sTD2DInputs[1], ivec2(i, 0), 0);
        float ds = (s - m.x) / uY.z;
        float dy = (y - m.y) / uY.w;
        float g = exp(-0.5 * (ds * ds + dy * dy));
        h += m.z * g;
        col += c.rgb * m.z * g;
        wsum += m.z * g;
    }
    col = wsum > 1e-4 ? col / wsum : vec3(0.0);
    fragColor = TDOutputSwizzle(vec4(col, h));
}
