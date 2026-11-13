shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D pixel_atlas : source_color, filter_nearest_mipmap, repeat_disable;
uniform float forest_depth = 0.0;
uniform float pigment_variation = 1.0;
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
    vec4 tex=texture(pixel_atlas,UV);
    ALPHA=tex.a;
    ALPHA_SCISSOR_THRESHOLD=.40;
    if(!FRONT_FACING)NORMAL=-NORMAL;
    vec3 paint=tex.rgb*pigment_variation;
    float haze=forest_depth*.16;
    vec3 mist=vec3(.24,.29,.19);
    paint=mix(paint,mist,haze);
    ALBEDO=paint*.84;
    EMISSION=paint*(.19+forest_depth*.015);
    ROUGHNESS=1.0;
    BACKLIGHT=vec3(.12);
}
