shader_type spatial;
render_mode diffuse_burley, specular_disabled;
uniform bool is_turf=false;
uniform bool is_valley=false;
uniform float depth_haze=0.0;
uniform sampler2D turf_paint:source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D rock_paint:source_color,filter_linear_mipmap_anisotropic;
#include "res://shaders/full_ink_pigment.gdshaderinc"
varying vec3 world_position;
varying vec3 world_normal;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 pigment=COLOR.rgb;
    // Smoothly lift the exposed-rock coverage on steep banks. Avoid a
    // per-triangle slope cutoff that would reveal the triangulation in pigment.
    float slope_rock=1.0-smoothstep(.73,.95,normalize(world_normal).y);
    if(is_turf){
        vec3 painted=texture(turf_paint,vec2((world_position.x+37.0)/44.0,(world_position.z+44.0)/44.0)).rgb;
        pigment=mix(pigment,painted,.82);
        if(is_valley){
            // A top-projected grass stroke should not stretch down a cliff.
            float rock=max(clamp(UV2.x,0.0,1.0),slope_rock);
            vec3 stone=cliff_pigment(world_position,world_normal);
            stone*=clamp(dot(COLOR.rgb,vec3(.2126,.7152,.0722))/.20,.88,1.03);
            pigment=mix(pigment,stone,rock);
            // Keep the connected valley's low bank, shoulder and wooded rear
            // distinct through broad pigment groups, without screen-space bands.
            float recess=.5+.5*sin(world_position.x*.25+world_position.z*.39);
            pigment*=mix(.90,1.04,recess)*(1.0-rock*.06);
        }
    }else{
        pigment=mix(pigment,cliff_pigment(world_position,world_normal),.88);
    }
    float haze=clamp(depth_haze+smoothstep(18.0,45.0,-world_position.z)*.15,0.0,.35);
    float rock_amount=is_turf?(is_valley?max(clamp(UV2.x,0.0,1.0),slope_rock):0.0):1.0;
    ALBEDO=mix(pigment*mix(.68,.82,rock_amount),vec3(.24,.29,.25),haze);
    EMISSION=mix(pigment*mix(.24,.075+.22*ink_sky_fill(world_normal),rock_amount),vec3(.24,.29,.25)*.25,haze);
    ROUGHNESS=1.0;
}
