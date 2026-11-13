shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D strata_color : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec3 pigment=texture(strata_color,UV).rgb;
    float wet=1.0-smoothstep(-.3,.30,world_position.y);
    ALBEDO=pigment*mix(.94,.77,wet);
    EMISSION=pigment*.07;
    ROUGHNESS=1.0;
    AO=1.0;
}
