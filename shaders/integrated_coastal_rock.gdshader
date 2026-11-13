shader_type spatial;
render_mode diffuse_burley,specular_disabled;
uniform sampler2D coastal_paint : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D coastal_contact : filter_linear_mipmap,repeat_disable;
uniform sampler2D brush_color : source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D cape_turf : source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D east_brush : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
varying vec3 world_position;
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
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec4 paint=texture(coastal_paint,vec2(fract(UV.x),clamp(UV.y,0.0,1.0)));
    vec3 rock=paint.rgb*vec3(1.12,.97,.93);
    // Quiet the large pigment patches so adjacent facets read as one stone mass.
    rock=mix(rock,vec3(.43,.29,.21),.12);
    float contact=mix(.56,1.0,texture(coastal_contact,UV2).r);
    float wet=1.0-smoothstep(-.45,.18,world_position.y);
    vec3 grass=edge_turf(world_position);float grove=forest_extent(world_position);
    ALBEDO=mix(rock*mix(1.0,.82,wet)*mix(.80,1.0,contact),grass*mix(.66,.90,grove),paint.a);
    EMISSION=mix(rock*.025*contact,grass*mix(.30,.025,grove),paint.a);
    AO=mix(contact,mix(1.0,.32,grove),paint.a);
    AO_LIGHT_AFFECT=.28*(1.0-paint.a);
    ROUGHNESS=1.0;
}
