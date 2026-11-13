shader_type sky;
render_mode use_half_res_pass;
#include "res://shaders/procedural_cloud_field.gdshaderinc"

uniform vec3 sky_top_color : source_color;
uniform vec3 sky_horizon_color : source_color;
uniform vec3 ground_bottom_color : source_color;
uniform vec3 ground_horizon_color : source_color;
uniform float sky_curve = .28;
uniform float ground_curve = .22;
uniform float cloud_cover : hint_range(0.0,1.0) = .48;

void sky(){
    vec3 base=pc_sky_base(EYEDIR,sky_top_color,sky_horizon_color,ground_bottom_color,ground_horizon_color,sky_curve,ground_curve);
    if(AT_CUBEMAP_PASS){
        // Stable mean radiance keeps local exposure independent of cloud sampling.
        COLOR=base;
    }else if(AT_HALF_RES_PASS){
        vec4 cloud=pc_clouds(normalize(EYEDIR),POSITION,TIME,cloud_cover,false);
        COLOR=cloud.rgb;
        ALPHA=cloud.a;
    }else{
        COLOR=mix(base,HALF_RES_COLOR.rgb,HALF_RES_COLOR.a);
    }
}
