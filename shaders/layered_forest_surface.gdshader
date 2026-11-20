shader_type spatial;
render_mode cull_disabled, diffuse_burley;
#include "res://shaders/forest_role_light.gdshaderinc"
#include "res://shaders/forest_bamboo_wind.gdshaderinc"
#include "res://shaders/cape_forest_floor.gdshaderinc"
uniform sampler2D painting : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
uniform vec4 grove_tint : source_color = vec4(1.0);
uniform float forest_air=0.0;
uniform float valley_air_strength=0.0;
uniform bool role_lighting=false;
uniform bool use_texture=true;
uniform bool vertex_tint=false;
uniform bool sand=false;
uniform bool foliage=false;
uniform bool actor_clearance=false;
uniform vec3 actor_focus=vec3(0.0);
uniform vec3 viewer_position=vec3(0.0);
uniform float wind_strength=0.0;
uniform bool coherent_bamboo=false;
uniform vec3 bamboo_root=vec3(0.0);
uniform float bamboo_height=9.0;
uniform float wind_seed=0.0;
uniform float wind_time_override=-1.0;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 authored_position;
varying vec3 world_position;
varying float optical_depth;
varying float continuity_upward;
void vertex(){
    continuity_upward=abs(NORMAL.y);
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    authored_position=(author_world_to_local*vec4(wp,1.0)).xyz;
    float t=wind_time_override>=0.0?wind_time_override:TIME;
    if(coherent_bamboo){
        VERTEX+=bamboo_bend(authored_position,bamboo_root,bamboo_height,wind_seed,t,wind_strength,0.0);
    }else{
        float gust=sin(t*.62+wp.x*.43+wp.z*.23)*.60+sin(t*1.07+wp.x*.81)*.23;
        VERTEX.x+=gust*UV2.x*wind_strength;
        VERTEX.z+=sin(t*.71+wp.x*.40)*UV2.x*wind_strength*.27;
    }
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    optical_depth=-(VIEW_MATRIX*vec4(world_position,1.0)).z;
}
void fragment(){
    vec3 color=(use_texture?texture(painting,UV).rgb:vec3(1.0))*tint.rgb;
    color=continuity_color(color,authored_position,continuity_upward);
    if(vertex_tint)color*=COLOR.rgb;
    if(foliage)color*=vec3(1.12,1.13,1.04);
    if(actor_clearance){
        vec3 ray=actor_focus-viewer_position;
        float t=dot(world_position-viewer_position,ray)/dot(ray,ray);
        float radius=length(world_position-viewer_position-ray*t);
        float mask=(1.0-smoothstep(.43,.95,radius))*step(.015,t)*(1.0-smoothstep(.96,1.0,t));
        // Stable spatial stipple clears only leaves crossing the actor; the
        // rest of each grove stays opaque and keeps its depth and shadow.
        float grain=fract(sin(dot(floor(world_position.xz*95.0)+floor(world_position.y*87.0),vec2(12.9898,78.233)))*43758.5453);
        if(grain<mask*.96)discard;
    }
    if(sand){
        float wet=1.0-smoothstep(-.11,.095,authored_position.y+.008*sin(authored_position.x*2.4));
        color=mix(color,color*vec3(.66,.73,.79),wet*.72);
        ROUGHNESS=mix(.97,.66,wet);
    }else{ROUGHNESS=.97;}
    // Air accumulates smoothly behind the activity band. Leaf tips and roots
    // receive their own view depth rather than one uniform color per grove.
    float distance_air=1.0-exp(-max(optical_depth-39.0,0.0)*.008);
    float air=vertex_tint?min(.24,distance_air+forest_air*smoothstep(42.0,78.0,optical_depth)):0.0;
    air=max(air,valley_air_strength*(1.0-exp(-max(optical_depth-38.0,0.0)*.04)));
    ALBEDO=color*grove_tint.rgb*(1.0-air);SPECULAR=.06;
    EMISSION=mix(vec3(.055,.073,.061),vec3(.18,.205,.15),step(.01,valley_air_strength))*air;
}
void light(){
    float diffuse=max(dot(NORMAL,LIGHT),0.0);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*diffuse*(role_lighting?role_sun(authored_position,TIME):1.0)/PI;
}
