// Soft centre-weighted mask for the camera presence: 1 in the middle, fading smoothly to 0 toward the edges.
uniform vec4 uV;   // x = focus radius (fraction of the frame height), y = aspect (w/h), z = vertical centre
out vec4 fragColor;
void main()
{
    vec2 p = vUV.st - vec2(0.5, uV.z);
    p.x *= uV.y;
    float d = length(p);
    float m = 1.0 - smoothstep(uV.x * 0.35, uV.x, d);
    fragColor = TDOutputSwizzle(vec4(m, m, m, 1.0));
}
