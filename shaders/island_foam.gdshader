shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
varying vec3 world_pos;
void vertex() { world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
    vec2 p = floor(world_pos.xz*22.0)/22.0;
    float drift = sin(p.x*2.9+p.y*1.7-TIME*.8);
    float rip = sin(UV.y*15.0-TIME*1.15+drift*1.5);
    float breakup = sin(p.x*9.0+p.y*6.0)*sin(p.y*12.0-p.x*4.0+TIME*.28);
    float edge = 1.0-smoothstep(.18,.86,UV.y);
    float line = smoothstep(.67,.94,rip);
    float beads = step(.55,breakup)*smoothstep(.7,1.0,edge);
    ALBEDO = vec3(.70,.84,.77);
    ALPHA = (line*.48*smoothstep(-.05,.55,breakup)+beads*.24)*edge;
}
