shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D fine_color : source_color, filter_linear_mipmap, repeat_disable;
uniform sampler2D surface_directions : filter_linear_mipmap, repeat_disable;
uniform float forest_depth = 0.0;
uniform float pigment_variation = 1.0;
uniform vec3 actor_position=vec3(0.0);
#include "res://shaders/forest_light_field.gdshaderinc"
#include "res://shaders/coastal_wind.gdshaderinc"
varying vec3 world_position;
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float weight=pow(clamp(UV2.x,0.0,1.0),1.7);
    vec2 bend=coastal_bend(world_position,TIME)*weight*.25;
    float flutter=sin(TIME*2.7+world_position.x*1.4+world_position.z)*.024*weight*coastal_gust(world_position,TIME);
    VERTEX+=(inverse(MODEL_MATRIX)*vec4(bend.x,flutter-dot(bend,bend)*.18,bend.y,0.0)).xyz;
}
void fragment(){
    vec4 tex=texture(fine_color,UV);
    ALPHA=tex.a;
    ALPHA_SCISSOR_THRESHOLD=.36;
    // Directions baked from our actual eastern culms/leaf folds, in card space.
    vec3 direction=texture(surface_directions,UV).xyz*2.0-1.0;
    direction.z=abs(direction.z);
    direction=normalize(mix(vec3(0.0,.35,.94),direction,.72));
    NORMAL=normalize((VIEW_MATRIX*MODEL_MATRIX*vec4(direction,0.0)).xyz);
    vec3 pigment=tex.rgb*mix(1.0,pigment_variation,.55);
    // Clear front culms frame a lighter interior; detailed leaves stay legible.
    float distance_layer=smoothstep(0.0,4.0,forest_depth);
    float interior=exp(-pow((forest_depth-1.6)/1.45,2.0));
    float front_shade=mix(.82,.69,smoothstep(2.0,4.0,forest_depth))+.18*interior;
    if(forest_depth<0.0)front_shade=.26;
    pigment*=mix(vec3(.83,.96,.91),vec3(.94,1.0,.98),distance_layer)*front_shade;
    float haze=pow(distance_layer,1.15)*.13;
    vec3 mist=vec3(.085,.125,.102);
    pigment=mix(pigment,mist,haze);
    ALBEDO=pigment*.94;
    EMISSION=pigment*.035;
    AO=mix(.70,.50,distance_layer);
    AO_LIGHT_AFFECT=0.0;
    ROUGHNESS=1.0;
    BACKLIGHT=vec3(.08);
}
void light(){
    float lambert=max(.0,(dot(NORMAL,LIGHT)+.22)/1.22);
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : forest_local_light_mask(world_position);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*lambert*mask/PI;
}
