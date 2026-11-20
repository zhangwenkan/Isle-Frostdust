shader_type spatial;
render_mode cull_disabled,diffuse_burley;
#include "res://shaders/forest_role_light.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D ground_paint:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 author_position;
void vertex(){author_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec2 floor_uv=(vec2(author_position.x,-author_position.z)-vec2(-68,4))/vec2(18,31);floor_uv.y=1.0-floor_uv.y;
    vec3 floor_color=texture(ground_paint,floor_uv).rgb;
    vec3 bank=texture(painting,vec2(UV.x,1.0-UV.y)).rgb;
    float irregular=sin(author_position.x*2.1-author_position.z*.6)*.035+sin(author_position.x*4.7)*.017;
    float upper=(1.0-smoothstep(.24+irregular,.66+irregular,UV.y))*.97;
    ALBEDO=mix(bank,floor_color,upper);ROUGHNESS=.97;SPECULAR=.06;
}
void light(){DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*role_sun(author_position,TIME)/PI;}
