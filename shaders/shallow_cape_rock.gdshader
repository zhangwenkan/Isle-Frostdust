shader_type spatial;
render_mode diffuse_burley,specular_disabled;
uniform sampler2D stone_paint : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D contact_shading : filter_linear_mipmap,repeat_disable;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec3 pigment=texture(stone_paint,UV).rgb;
    float contact=mix(.46,1.0,texture(contact_shading,UV2).r);
    float wet=1.0-smoothstep(-2.16,-1.75,world_position.y);
    pigment=mix(pigment,pigment*vec3(.65,.71,.70),wet*.67);
    ALBEDO=pigment*mix(.77,1.0,contact);
    EMISSION=(pigment*.16+vec3(.023,.030,.032))*contact;
    AO=contact;AO_LIGHT_AFFECT=.5;ROUGHNESS=1.0;
}
