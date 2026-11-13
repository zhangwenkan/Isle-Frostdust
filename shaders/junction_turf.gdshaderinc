#include "res://shaders/cape_layout.gdshaderinc"
#include "res://shaders/forest_light_field.gdshaderinc"
float coast_old_route(float x){
    float start=.4+sin(-20.7*.25)*.44;
    if(x<=-18.5)return start-(x+20.7)*5.0/9.0;
    if(x>=-12.5)return .4+sin(x*.25)*.44;
    float t=(x+18.5)/6.0;float a=start-2.2*5.0/9.0;float b=.4+sin(-12.5*.25)*.44;
    return (2.0*t*t*t-3.0*t*t+1.0)*a+(t*t*t-2.0*t*t+t)*6.0*(-5.0/9.0)+(-2.0*t*t*t+3.0*t*t)*b+(t*t*t-t*t)*6.0*.11*cos(-12.5*.25);
}
vec3 edge_turf(vec3 p){
    float x=extended_cape_source_x(p.x);
    float z=p.z+(coast_old_route(x)-.25)*(1.0-smoothstep(2.8,4.1,p.x));
    vec3 base=texture(brush_color,vec2((x+20.0)/26.0,(z+7.0)/14.0)).rgb;
    vec3 cape=texture(cape_turf,vec2((x+26.0)/15.0,(z+6.0)/12.0)).rgb;
    base=mix(base,cape,1.0-smoothstep(-12.5,-11.2,x));
    vec3 corner=texture(cape_turf,vec2((x+26.0)/15.0,(z+8.4)/12.0)).rgb;
    base=mix(base,corner,(1.0-smoothstep(-25.5,-24.15,p.x))*.92);
    vec3 east=texture(east_brush,vec2((p.x+1.0)/30.0,(p.z+7.0)/14.0)).rgb;
    return mix(base,east,smoothstep(-1.0,2.7,p.x));
}
