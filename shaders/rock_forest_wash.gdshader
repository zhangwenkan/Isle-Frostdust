shader_type spatial;
render_mode cull_disabled,diffuse_burley;
#include "res://shaders/forest_role_light.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D normal_paint:hint_normal,filter_linear_mipmap_anisotropic,repeat_disable;
uniform mat4 author_world_to_local=mat4(1.0);
uniform float normal_strength=.72;
uniform bool use_texture=true;
uniform bool use_normal=true;
uniform vec4 tint:source_color=vec4(.45,.46,.42,1.0);
uniform bool stone_step=false;
varying vec3 author_position;
void vertex(){author_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    ALBEDO=use_texture?texture(painting,UV).rgb:tint.rgb;
    if(stone_step)ALBEDO*=COLOR.rgb;
    if(use_normal){NORMAL_MAP=texture(normal_paint,UV).rgb;NORMAL_MAP_DEPTH=normal_strength;}
    ROUGHNESS=.94;SPECULAR=.06;
}
void light(){
    float wrap=stone_step?.10:0.0;
    float diffuse=max((dot(NORMAL,LIGHT)+wrap)/(1.0+wrap),0.0);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*diffuse*role_sun(author_position,TIME)/PI;
}
