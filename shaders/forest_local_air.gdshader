shader_type fog;
uniform float density=0.025;
void fog(){
    vec3 p=WORLD_POSITION;
    float drift=sin(p.x*.32+p.z*.22+TIME*.055)*.22;
    drift+=sin(p.x*.63-p.z*.19+p.y*.41-TIME*.036)*.14;
    float edge=smoothstep(0.0,2.0,-SDF);
    DENSITY=density*edge*(.68+drift);
    ALBEDO=vec3(.62,.68,.53);
    EMISSION=vec3(0.0);
}
