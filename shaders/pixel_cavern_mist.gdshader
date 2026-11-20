shader_type fog;
uniform vec3 fog_tint:source_color=vec3(.65,.76,.73);
uniform float strength=.045;
void fog(){
    vec3 p=WORLD_POSITION;
    float lobe=.55+.22*sin(p.x*.18+sin(p.z*.15)+TIME*.012)+.15*sin(p.z*.24-p.x*.11-TIME*.009);
    float edge=1.0-smoothstep(.22,.50,abs(UVW.y-.5));
    float sides=(1.0-smoothstep(.32,.50,abs(UVW.x-.5)))*(1.0-smoothstep(.30,.50,abs(UVW.z-.5)));
    DENSITY=strength*edge*sides*max(.1,lobe);
    ALBEDO=fog_tint;
    EMISSION=fog_tint*.46;
}
