shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never,fog_disabled;
#include "res://shaders/forest_sun_field.gdshaderinc"
#include "res://shaders/forest_coastal_edge.gdshaderinc"
uniform float opacity=1.0;
uniform float layer=0.0;
uniform vec4 fog_color:source_color=vec4(.59,.65,.53,1.0);
uniform float time_override=-1.0;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 authored_position;
float mist_hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float mist_noise(vec2 p){
    vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);
    return mix(mix(mist_hash(i),mist_hash(i+vec2(1,0)),f.x),mix(mist_hash(i+vec2(0,1)),mist_hash(i+vec2(1,1)),f.x),f.y);
}
void vertex(){authored_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    float t=time_override>=0.0?time_override:TIME;
    vec2 p=vec2(authored_position.x*.075,UV.y*2.6)+vec2(layer*3.7,t*.034);
    float large=mist_noise(p+vec2(sin(t*.047+layer)*.35,0));
    float detail=mist_noise(p*2.1+vec2(t*.017,-t*.012));
    float height=.48+.14*sin(authored_position.x*.14+layer*1.8+t*.055)+.12*(large-.5);
    float veil=exp(-pow((UV.y-height)/(.23+.08*large),2.0));
    float edges=smoothstep(.0,.12,UV.x)*(1.0-smoothstep(.88,1.0,UV.x))*smoothstep(.0,.14,UV.y)*(1.0-smoothstep(.88,1.0,UV.y));
    float pockets=smoothstep(.17,.79,large*.72+detail*.28);
    float sun=forest_aperture(authored_position,t);
    vec3 shade=fog_color.rgb*(.57+.08*large)+forest_sun_tint.rgb*sun*.20;
    ALBEDO=mix(fog_color.rgb*(.92+.08*large),shade,forest_light_strength);
    ALPHA=veil*edges*pockets*opacity*(.30-layer*.018)*terminal_forest_edge(authored_position);
}
