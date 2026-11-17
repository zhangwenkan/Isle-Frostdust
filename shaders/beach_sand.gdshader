shader_type spatial;
render_mode cull_disabled, diffuse_burley;
#include "res://shaders/beach_swash_field.gdshaderinc"
uniform sampler2D sand_map:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
void fragment(){
    vec3 dry=texture(sand_map,UV).rgb;
    float value=dot(dry,vec3(.2126,.7152,.0722));
    dry=mix(vec3(value),dry,.90)*.87;
    float wet=swash_wetness(UV2);
    // A wet substrate keeps the same brush detail. It darkens after run-up
    // and dries behind the receding film; its texture coordinates never move.
    ALBEDO=mix(dry,dry*vec3(.60,.58,.59),wet*.79);
    ROUGHNESS=mix(.96,.72,wet);SPECULAR=.08;
}
