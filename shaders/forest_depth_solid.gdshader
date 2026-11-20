shader_type spatial;
render_mode unshaded,cull_disabled,fog_disabled;
#include "res://shaders/forest_sun_field.gdshaderinc"
#include "res://shaders/forest_coastal_edge.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap,repeat_disable;
uniform float opacity=1.0;
uniform float time_override=-1.0;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 authored_position;
void vertex(){authored_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    // The fully enclosed forest has an opaque depth-bearing back painting.
    // A stable fine stipple only supplies the transition from the coast.
    float grain=fract(sin(dot(floor(FRAGCOORD.xy),vec2(12.9898,78.233)))*43758.5453);
    float visible=opacity*terminal_forest_edge(authored_position);
    if(visible<.001 || grain>visible)discard;
    float t=time_override>=0.0?time_override:TIME;
    vec3 c=texture(painting,UV).rgb;
    ALBEDO=forest_painted_light(c,authored_position,t);
}
