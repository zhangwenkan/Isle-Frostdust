shader_type spatial;
render_mode cull_disabled,diffuse_burley;
#include "res://shaders/forest_role_light.gdshaderinc"
#include "res://shaders/cape_forest_floor.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform bool use_texture=true;
uniform vec4 tint:source_color=vec4(1.0);
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 author_position;
varying float upward;
void vertex(){
    author_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    upward=abs(NORMAL.y);
}
void fragment(){
    vec3 color=(use_texture?texture(painting,UV).rgb:tint.rgb)*.93;
    ALBEDO=continuity_color(color,author_position,upward);ROUGHNESS=.97;SPECULAR=.06;
}
void light(){
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*role_sun(author_position,TIME)/PI;
}
