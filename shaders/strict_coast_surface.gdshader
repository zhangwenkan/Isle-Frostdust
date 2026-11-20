shader_type spatial;
render_mode cull_disabled,diffuse_burley;
#include "res://shaders/forest_role_light.gdshaderinc"
#include "res://shaders/forest_bamboo_wind.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D normal_paint:hint_normal,filter_linear_mipmap_anisotropic,repeat_enable;
uniform bool use_normal=false;
uniform bool use_texture=true;
uniform vec4 tint:source_color=vec4(1.0);
uniform bool bamboo=false;
uniform bool leaf_surface=false;
uniform bool grass=false;
uniform mat4 author_world_to_local=mat4(1.0);
uniform vec3 bamboo_root=vec3(0.0);
uniform float bamboo_height=10.0;
uniform float wind_seed=0.0;
uniform float wind_strength=.5;
uniform float wind_time_override=-1.0;
uniform vec3 actor_focus=vec3(0.0);
uniform vec3 viewer_position=vec3(0.0);
varying vec3 author_position;
varying vec3 world_position;
void vertex(){
    author_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float t=wind_time_override>=0.0?wind_time_override:TIME;
    if(bamboo)VERTEX+=bamboo_bend(author_position,bamboo_root,bamboo_height,wind_seed,t,wind_strength,UV2.y);
    if(grass){VERTEX.x+=sin(t*1.18+author_position.x*.83+author_position.z*.57)*UV2.x*.035;}
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    author_position=(author_world_to_local*vec4(world_position,1.0)).xyz;
}
void fragment(){
    ALBEDO=use_texture?texture(painting,UV).rgb:tint.rgb;
    ROUGHNESS=leaf_surface?.83:.91;SPECULAR=leaf_surface?.12:.06;
    if(use_normal){NORMAL_MAP=texture(normal_paint,UV).rgb;NORMAL_MAP_DEPTH=.28;}
    if(bamboo){
        vec3 ray=actor_focus-viewer_position;
        float t=dot(world_position-viewer_position,ray)/max(dot(ray,ray),.001);
        float distance=length(world_position-viewer_position-ray*t);
        float mask=(1.0-smoothstep(.42,.85,distance))*step(.015,t)*(1.0-smoothstep(.94,1.0,t));
        float grain=fract(sin(dot(floor(world_position.xz*95.0)+floor(world_position.y*87.0),vec2(12.9898,78.233)))*43758.5453);
        if(grain<mask*.96)discard;
    }
}
void light(){
    float ndl=max(dot(NORMAL,LIGHT),0.0);
    float diffuse=leaf_surface?(.18+.82*ndl):ndl;
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*diffuse*role_sun(author_position,TIME)/PI;
}
