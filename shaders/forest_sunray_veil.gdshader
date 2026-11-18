shader_type spatial;
render_mode unshaded,blend_add,cull_disabled,depth_draw_never,fog_disabled,shadows_disabled;
#include "res://shaders/forest_sun_field.gdshaderinc"
uniform mat4 author_world_to_local=mat4(1.0);
uniform float opacity=1.0;
uniform float veil_strength=.14;
uniform float layer=0.0;
varying vec3 authored_position;
void vertex(){authored_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    float sun=forest_aperture(authored_position,TIME);
    float lateral=smoothstep(.0,.20,UV.x)*(1.0-smoothstep(.80,1.0,UV.x));
    float ends=smoothstep(.0,.23,UV.y)*(1.0-smoothstep(.74,1.0,UV.y));
    float air=.65+.35*forest_field_noise(authored_position.xz*.25+vec2(layer*3.7,authored_position.y*.19));
    ALBEDO=forest_sun_tint.rgb;
    ALPHA=sun*lateral*ends*air*veil_strength*opacity*forest_light_strength;
}
