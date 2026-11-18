shader_type spatial;
render_mode cull_disabled, diffuse_burley;
#include "res://shaders/forest_role_light.gdshaderinc"
#include "res://shaders/forest_bamboo_wind.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform mat4 author_world_to_local=mat4(1.0);
uniform vec3 actor_focus=vec3(0.0);
uniform vec3 viewer_position=vec3(0.0);
uniform float wind_strength=.18;
uniform vec3 bamboo_root=vec3(0.0);
uniform float bamboo_height=9.0;
uniform float wind_seed=0.0;
uniform float wind_time_override=-1.0;
uniform bool foreground=false;
varying vec3 authored_position;
varying vec3 world_position;
void vertex(){
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    vec3 p=(author_world_to_local*vec4(wp,1.0)).xyz;
    float t=wind_time_override>=0.0?wind_time_override:TIME;
    VERTEX+=bamboo_bend(p,bamboo_root,bamboo_height,wind_seed,t,wind_strength,UV2.y);
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    authored_position=(author_world_to_local*vec4(world_position,1.0)).xyz;
}
void fragment(){
    vec4 sample_color=texture(painting,UV);
    ALPHA=sample_color.a;ALPHA_SCISSOR_THRESHOLD=.40;
    vec3 ray=actor_focus-viewer_position;
    float t=dot(world_position-viewer_position,ray)/max(dot(ray,ray),.001);
    float radius=length(world_position-viewer_position-ray*t);
    float mask=(1.0-smoothstep(.43,.95,radius))*step(.015,t)*(1.0-smoothstep(.96,1.0,t));
    float grain=fract(sin(dot(floor(world_position.xz*95.0)+floor(world_position.y*87.0),vec2(12.9898,78.233)))*43758.5453);
    if(grain<mask*.96)discard;
    ALBEDO=sample_color.rgb*(foreground?vec3(.72,.78,.65):vec3(1.0));
    ROUGHNESS=.97;SPECULAR=.03;
}
void light(){
    float diffuse=.28+.72*max(dot(NORMAL,LIGHT),0.0);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*diffuse*role_sun(authored_position,TIME)/PI;
}
