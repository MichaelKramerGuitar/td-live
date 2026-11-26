// Harmony Galaxy, Attractor texture: a soft round particle, added (blending one + one).
in vec4 vColor;
in vec2 vQ;
out vec4 fragColor;
void main()
{
    float a = exp(-3.0 * dot(vQ, vQ));
    fragColor = TDOutputSwizzle(vec4(vColor.rgb * a, a));
}
