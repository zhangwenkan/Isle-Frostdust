shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform bool use_vertex_wash=true;
#include "res://shaders/full_ink_pigment.gdshaderinc"
#include "res://shaders/forest_light_field.gdshaderinc"
varying vec3 world_position;
varying vec3 world_normal;
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 pigment=cliff_pigment(world_position,world_normal);
    // Retain large mineral-value groups, with restrained contrast across the
    // connected bedrock. Existing silhouettes provide the structural edges.
    float deposit=use_vertex_wash?clamp(dot(COLOR.rgb,vec3(.2126,.7152,.0722))/.20,.84,1.05):1.0;
    pigment*=deposit;
    float grove=forest_extent(world_position);
    ALBEDO=pigment*mix(.82,.52,grove);
    EMISSION=pigment*mix(.075+.22*ink_sky_fill(world_normal),.018,grove);
    AO=mix(1.0,.28,grove);
    AO_LIGHT_AFFECT=0.0;
    ROUGHNESS=1.0;
}
void light(){
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : forest_local_light_mask(world_position);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*mask/PI;
}
