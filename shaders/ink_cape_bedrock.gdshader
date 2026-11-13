shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D brush_color : source_color, filter_linear_mipmap_anisotropic;
varying vec3 world_position;
varying vec3 stone_world_normal;
#include "res://shaders/cape_layout.gdshaderinc"
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    stone_world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    // The same clean gray-green wash and sky-fill direction as the sample rocks.
    // Retain broad authored cliff colors as a restrained mineral wash, not noise.
    float cape_weight=1.0-smoothstep(-18.0,-13.0,extended_cape_source_x(world_position.x));
    vec3 pigment=texture(brush_color,UV).rgb;
    float deposit=clamp(dot(COLOR.rgb,vec3(.2126,.7152,.0722))/.20,.78,1.08);
    pigment*=deposit;
    float sky_fill=max(dot(normalize(stone_world_normal),normalize(vec3(-.65,.70,.45))),0.0);
    ALBEDO=mix(COLOR.rgb,pigment*.82,cape_weight);
    EMISSION=pigment*(.075+.22*sky_fill)*cape_weight;
    ROUGHNESS=1.0;
}
