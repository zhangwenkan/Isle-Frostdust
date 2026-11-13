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
    if(AT_CUBEMAP_PASS){
        COLOR=pc_sky_base(EYEDIR,sky_top_color,sky_horizon_color,ground_bottom_color,ground_horizon_color,sky_curve,ground_curve);
    }else if(AT_HALF_RES_PASS){
        vec4 cloud=pc_clouds(normalize(EYEDIR),POSITION,TIME,cloud_cover,true);
        COLOR=cloud.rgb;
        ALPHA=cloud.a;
    }else{
        vec3 d=normalize(EYEDIR);
        float az=atan(-d.x,-d.z)*57.29578;
        float el=asin(clamp(d.y,-1.0,1.0))*57.29578;
        vec3 col=mix(vec3(.745,.749,.718),vec3(.80,.744,.622),smoothstep(-3.5,10.0,el));
        float r=length(vec2((az-9.5)*cos(radians(el)),el-4.2));
        col=mix(col,vec3(.83,.40,.30),exp(-r*r/100.0)*.16);
        vec3 clouded=mix(pc_display_to_scene(col),HALF_RES_COLOR.rgb,HALF_RES_COLOR.a);
        // Art-directed sunset: the disc is composited after the sky clouds.
        // Its pigment and opacity do not depend on the cloud density behind it.
        vec3 sun_pigment=mix(col,vec3(.78,.27,.19),.84);
        float disc=1.0-smoothstep(1.20,1.42,r);
        COLOR=mix(clouded,pc_display_to_scene(sun_pigment),disc);
    }
}
