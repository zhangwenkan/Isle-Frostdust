// Authored coordinates for the western forest; broad light openings, quiet motion.
#include "res://shaders/forest_sun_field.gdshaderinc"
float role_extent(vec3 p){
    return smoothstep(7.0,14.0,-p.x)*(1.0-smoothstep(61.0,68.0,-p.x))*smoothstep(-3.0,5.0,-p.z);
}
float role_sun(vec3 p,float t){
    float depth=-p.z;
    float opening=.55+.27*sin(p.x*.42+depth*.17)+.13*sin(p.x*.77-depth*.21);
    float road=1.0-smoothstep(1.0,3.6,abs(depth-12.8));
    float near_shade_weight=1.0-smoothstep(8.5,11.0,depth);
    float value=clamp(opening+road*.28-near_shade_weight*.31,.15,1.0);
    float shared=.60+.85*forest_aperture(p,t);
    value*=mix(1.0,shared,forest_light_strength);
    return mix(1.0,value,role_extent(p));
}
