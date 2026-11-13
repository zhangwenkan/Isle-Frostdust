shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D floor_paint : source_color, filter_linear_mipmap;
uniform bool is_side=false;
#include "res://shaders/full_ink_pigment.gdshaderinc"
#include "res://shaders/forest_light_field.gdshaderinc"
varying vec3 world_position;
varying vec3 world_normal;
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 grass=texture(floor_paint,world_position.xz/12.0).rgb;
    vec3 rock=cliff_pigment(world_position,world_normal)*vec3(.95,.98,.90);
    float steep=1.0-smoothstep(.35,.82,abs(world_normal.y));
    float rock_weight=is_side ? .92 : steep*.72;
    vec3 pigment=mix(grass,rock,rock_weight);
    vec4 contacts[3]=vec4[3](vec4(-11.06,-5.15,.88,.63),vec4(-9.24,-5.06,.47,.41),vec4(-4.86,-5.12,.79,.56));
    float contact=0.0;
    for(int i=0;i<3;i++){
        vec2 q=(world_position.xz-contacts[i].xy)/contacts[i].zw;
        contact=max(contact,exp(-dot(q,q)*1.45)*.20);
    }
    pigment*=1.0-contact;
    float forest_core=smoothstep(-18.0,-14.0,world_position.x)*(1.0-smoothstep(-4.0,1.0,world_position.x));
    ALBEDO=pigment*mix(.96,.86,forest_core);
    EMISSION=pigment*.035;
    ROUGHNESS=1.0;
    AO=mix(1.0,.75,forest_core);
    AO_LIGHT_AFFECT=0.0;
}
void light(){
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : 1.0;
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*mask/PI;
}
