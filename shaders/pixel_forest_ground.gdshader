shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D floor_paint : source_color, filter_nearest_mipmap;
uniform sampler2D edge_paint : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D cape_turf : source_color, filter_linear_mipmap_anisotropic;
#include "res://shaders/cape_layout.gdshaderinc"
#include "res://shaders/forest_light_field.gdshaderinc"
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec3 forest=texture(floor_paint,world_position.xz/12.0).rgb;
    float source_x=cape_source_x(world_position.x);
    vec3 edge=texture(edge_paint,vec2((source_x+20.0)/26.0,(world_position.z+7.0)/14.0)).rgb;
    vec3 cape=texture(cape_turf,vec2((source_x+26.0)/15.0,(world_position.z+6.0)/12.0)).rgb;
    edge=mix(edge,cape,1.0-smoothstep(-12.5,-11.2,source_x));
    float forest_mix=smoothstep(1.85,5.8,-world_position.z+.32*sin(world_position.x*1.1));
    vec3 paint=mix(edge,forest,forest_mix);
    float depth=1.0-smoothstep(-17.0,-3.0,world_position.z);
    paint=mix(paint,vec3(.16,.205,.145),depth*.34);
    vec4 contacts[3]=vec4[3](vec4(-11.06,-5.15,.88,.63),vec4(-9.24,-5.06,.47,.41),vec4(-4.86,-5.12,.79,.56));
    float contact=0.0;
    for(int i=0;i<3;i++){
        vec2 relative=(world_position.xz-contacts[i].xy)/contacts[i].zw;
        contact=max(contact,exp(-dot(relative,relative)*1.45)*.24);
    }
    paint*=1.0-contact;
    float west_grove=smoothstep(-17.5,-14.0,world_position.x)*(1.0-smoothstep(.2,3.0,world_position.x));
    ALBEDO=paint*.83;
    EMISSION=paint*.025;
    AO=mix(.55,.24,smoothstep(2.0,12.0,-world_position.z));
    AO_LIGHT_AFFECT=0.0;
    ROUGHNESS=1.0;
}
void light(){
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : forest_local_light_mask(world_position);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*mask/PI;
}
