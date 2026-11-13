// Sumiro hill paintings on the Blender-authored comparison layer.
// See assets/sumiro/PROVENANCE.md for third-party source and licence status.
shader_type spatial;
#include "res://shaders/sunset_sea_mist.gdshaderinc"
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D painting : filter_linear_mipmap_anisotropic;
uniform sampler2D scene_depth : hint_depth_texture, filter_nearest;
varying vec3 world_position;

void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
}
vec3 display_to_scene(vec3 c){
    vec3 y=mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a=2.51-2.43*y,b=.03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}
void fragment(){
    float raw=texture(scene_depth,SCREEN_UV).r;
    vec4 behind=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.0-1.0,raw,1.0);
    if(raw>.00001 && -behind.z/behind.w<55.0)discard;
    vec4 m=texture(painting,UV);
    if(m.a<.008)discard;
    float gray=dot(m.rgb,vec3(.2126,.7152,.0722));
    vec3 warm=vec3(gray)*vec3(1.05,1.015,.95);
    // Let the painted foothills dissolve into the same warm sea haze as the water.
    // Use world height, so the blend stays attached to the landscape while walking.
    float valley=sunset_valley_height(world_position.xz);
    float clear_peak=smoothstep(-3.0,7.0,world_position.y-valley);
    vec3 haze=vec3(.63,.73,.75);
    ALBEDO=display_to_scene(mix(haze,warm,mix(.28,1.0,clear_peak)));
    // Pale paper in the lower painting must not become a cream coast-wide strip.
    float lower_paper=1.0-smoothstep(.62,.92,gray);
    ALPHA=m.a*smoothstep(-7.0,3.0,world_position.y-valley)
        *mix(lower_paper,1.0,clear_peak);
}
