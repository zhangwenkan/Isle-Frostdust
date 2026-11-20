shader_type spatial;
render_mode unshaded,cull_disabled,depth_prepass_alpha,fog_disabled;
#include "res://shaders/forest_sun_field.gdshaderinc"
#include "res://shaders/forest_coastal_edge.gdshaderinc"
uniform sampler2D painting:source_color,filter_linear_mipmap,repeat_disable;
uniform float opacity=1.0;
uniform float layer=0.0;
uniform float time_override=-1.0;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 authored_position;
void vertex(){
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    authored_position=(author_world_to_local*vec4(wp,1.0)).xyz;
    // Only the soft upper silhouettes breathe, at different depth-dependent rates.
    float weight=smoothstep(.22,.75,1.0-UV.y);
    float t=time_override>=0.0?time_override:TIME;
    VERTEX.x+=sin(t*(.095+layer*.027)+wp.x*.19)*weight*.045;
}
void fragment(){
    vec4 c=texture(painting,UV);
    float t=time_override>=0.0?time_override:TIME;
    ALBEDO=forest_painted_light(c.rgb,authored_position,t);
    ALPHA=c.a*opacity*terminal_forest_edge(authored_position);
}
