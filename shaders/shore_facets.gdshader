shader_type spatial;
render_mode diffuse_burley, specular_disabled;
uniform sampler2D rock_faces : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec3 pigment=texture(rock_faces,UV).rgb;
    float wet=1.0-smoothstep(-.32,.18,world_position.y);
    ALBEDO=pigment*mix(1.0,.84,wet);
    EMISSION=pigment*.035;
    ROUGHNESS=1.0;
}
