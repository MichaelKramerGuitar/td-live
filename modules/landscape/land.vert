// Fretboard landscape (GLSL MAT, vertex). The geometry is a 1x1 grid in the XY plane; this shader lays it
// along the neck and sinks it into the field's wells.
//   u (x+0.5) -> string coordinate between uMap.x and uMap.y (0 = low string)
//   v (y+0.5) -> distance from the nut: linear (terrain lines) or snapped to frets (uMap.z = 1)
uniform sampler2D sField;
uniform vec4 uMap;     // s min, s max, fret mode, frets
uniform vec4 uY;       // ymin, ymax
uniform vec4 uWorld;   // string spacing, neck length, well depth, -
out Vertex { vec3 color; float depth; float h; } oVert;
void main()
{
    float u = P.x + 0.5, v = P.y + 0.5;
    float s = mix(uMap.x, uMap.y, u);
    float ymax = uY.y;
    float y;
    if (uMap.z > 0.5) {
        float n = floor(v * uMap.w + 0.5);
        y = 1.0 - pow(2.0, -n / 12.0);
    } else {
        y = mix(ymax, uY.x, v);            // v = 0 at the bridge end (near), 1 past the nut (far)
    }
    vec2 tc = vec2((s + 0.5) / 6.0, (y - uY.x) / (uY.y - uY.x));
    vec4 f = texture(sField, tc);
    vec3 world = vec3((s - 2.5) * uWorld.x, -f.a * uWorld.z, -(ymax - y) * uWorld.y);
    vec4 worldSpacePos = TDDeform(world);
    gl_Position = TDWorldToProj(worldSpacePos);
    oVert.color = f.rgb;
    oVert.h = f.a;
    oVert.depth = clamp((ymax - y) / (ymax - uY.x), 0.0, 1.0);
}
