shader_type spatial;
render_mode diffuse_burley, specular_disabled;
uniform sampler2D brush_color : source_color, filter_linear_mipmap_anisotropic;
varying vec3 world_position;
varying vec3 world_normal;
#include "res://shaders/forest_light_field.gdshaderinc"
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 brush=texture(brush_color,UV).rgb;
    float value=dot(brush,vec3(.2126,.7152,.0722));
    vec3 stone=mix(vec3(.092,.111,.099),vec3(.23,.25,.205),smoothstep(.08,.58,value));
    // Broad moss patches follow upper-facing stone surfaces and raised edges.
    // The original sparse structural strokes remain in the base paint.
    float patches=.58+.22*sin(world_position.x*1.8+world_position.z*.9)+.15*sin(world_position.z*2.1);
    float up=smoothstep(.14,.78,world_normal.y);
    float moss=up*smoothstep(.30,.70,UV2.x)*smoothstep(.22,.76,patches);
    vec3 pigment=mix(stone,vec3(.18,.235,.09),moss*.86);
    pigment*=mix(.76,1.0,smoothstep(.04,.30,UV2.x));
    ALBEDO=pigment*.95;
    EMISSION=pigment*.025;
    AO=.38;
    AO_LIGHT_AFFECT=0.0;
    ROUGHNESS=1.0;
}
void light(){
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : forest_local_light_mask(world_position);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*mask/PI;
}
