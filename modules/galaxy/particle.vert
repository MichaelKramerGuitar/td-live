// Harmony Galaxy, Attractor texture: each instance is one particle, a small camera-facing square (billboard)
// positioned by the simulation TOP.
uniform vec4 uPoint;      // x = particle size (world units)
out vec4 vColor;
out vec2 vQ;
void main()
{
    vec4 centre = TDDeform(vec3(0.0));                      // the instance's world position
    int ci = TDCameraIndex();
    vec4 viewPos = uTDMats[ci].cam * centre;
    viewPos.xy += P.xy * uPoint.x;
    gl_Position = uTDMats[ci].proj * viewPos;
    // particles right in front of the lens fade out (the body cam rides inside the flow: no white-out)
    float near = smoothstep(0.03, 0.25, -viewPos.z);
    vColor = TDInstanceColor(Cd) * near;
    vQ = P.xy * 2.0;
}
