shader_type spatial;
render_mode diffuse_burley,specular_disabled;
uniform sampler2D mineral_paint : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D contact_shading : filter_linear_mipmap,repeat_disable;
uniform bool top_surface=false;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec3 pigment=texture(mineral_paint,UV).rgb;
    pigment*=vec3(1.12,.97,.93);
    float contact=mix(.35,1.0,texture(contact_shading,UV2).r);
    float wet=1.0-smoothstep(-.45,.18,world_position.y);
    ALBEDO=pigment*mix(1.0,.82,wet)*mix(.72,1.0,contact);
    EMISSION=pigment*.025*contact;
    AO=contact;
    AO_LIGHT_AFFECT=.45;
    ROUGHNESS=1.0;
}
