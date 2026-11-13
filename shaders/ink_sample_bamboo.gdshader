shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform bool is_leaf=false;
uniform bool is_grass=false;
uniform float depth_haze=0.0;
#include "res://shaders/coastal_wind.gdshaderinc"
#include "res://shaders/forest_light_field.gdshaderinc"
varying vec3 world_position;
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float weight=pow(clamp(UV2.x,0.0,1.0),1.65);
    vec2 bend=coastal_bend(world_position,TIME)*weight*(is_grass?.075:.37);
    VERTEX.xz+=bend;
    VERTEX.y-=dot(bend,bend)*.14;
    if(is_leaf){VERTEX.y+=sin(TIME*3.1+world_position.x*2.3+world_position.z*1.7)*.026*weight*coastal_gust(world_position,TIME);}
}
void fragment(){
    if(!FRONT_FACING)NORMAL=-NORMAL;
    vec3 pigment=COLOR.rgb;
    if(is_leaf || is_grass){
        // Brush edges follow UV0 and therefore remain attached during bending.
        float side=abs(UV.x-.5)*2.0;
        float edge=smoothstep(.72,.98,side)*smoothstep(.08,.25,UV.y);
        float vein=(1.0-smoothstep(.012,.055,abs(UV.x-.49)))*smoothstep(.15,.35,UV.y)*(1.0-smoothstep(.65,.91,UV.y));
        pigment=mix(pigment,pigment*vec3(.32,.39,.33),edge*.82+vein*.24);
    }else{
        float side=1.0-smoothstep(.12,.48,abs(dot(normalize(NORMAL),normalize(VIEW))));
        pigment=mix(pigment,pigment*vec3(.38,.46,.38),side*.75);
    }
    ALBEDO=pigment*.76;
    EMISSION=pigment*mix(.23,.025,forest_extent(world_position));
    AO=mix(1.0,.32,forest_extent(world_position));
    AO_LIGHT_AFFECT=0.0;
    ALBEDO=mix(ALBEDO,vec3(.19,.26,.24)*.75,depth_haze);
    EMISSION=mix(EMISSION,vec3(.19,.26,.24)*.65,depth_haze);
    ROUGHNESS=1.0;
    BACKLIGHT=vec3(0.0);
}
void light(){
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : forest_local_light_mask(world_position);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*mask/PI;
}
