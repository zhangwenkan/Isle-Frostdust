shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D original_color : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D original_normal : hint_normal, filter_linear_mipmap_anisotropic;
uniform sampler2D brush_color : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D cape_turf : source_color, filter_linear_mipmap_anisotropic;
uniform sampler2D east_brush : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform bool coastal_edge_enabled=false;
uniform sampler2D coastal_edge_paint : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D junction_edge_paint : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D shallow_cape_surface : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
varying vec3 world_position;
#include "res://shaders/cape_layout.gdshaderinc"
#include "res://shaders/forest_light_field.gdshaderinc"
float old_route(float x){
    float start=.4+sin(-20.7*.25)*.44;
    if(x<=-18.5)return start-(x+20.7)*5.0/9.0;
    if(x>=-12.5)return .4+sin(x*.25)*.44;
    float t=(x+18.5)/6.0;
    float a=start-2.2*5.0/9.0;float b=.4+sin(-12.5*.25)*.44;
    return (2.0*t*t*t-3.0*t*t+1.0)*a+(t*t*t-2.0*t*t+t)*6.0*(-5.0/9.0)+(-2.0*t*t*t+3.0*t*t)*b+(t*t*t-t*t)*6.0*.11*cos(-12.5*.25);
}
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec3 paint_position=vec3(extended_cape_source_x(world_position.x),world_position.yz);
    float paint_z=world_position.z+(old_route(paint_position.x)-.25)*(1.0-smoothstep(2.8,4.1,world_position.x));
    vec2 painting_uv=vec2((paint_position.x+20.0)/26.0,(paint_z+7.0)/14.0);
    vec3 brush=texture(brush_color,painting_uv).rgb;
    // Continue the same pigment and lighting treatment all the way to the cape.
    // This overlap lies inside both paintings, avoiding a stretched border texel.
    float cape_weight=1.0-smoothstep(-12.5,-11.2,paint_position.x);
    vec3 cape=texture(cape_turf,vec2((paint_position.x+26.0)/15.0,(paint_z+6.0)/12.0)).rgb;
    brush=mix(brush,cape,cape_weight);
    // Grass occupies the broad outer corner; the lane still runs horizontally.
    vec3 cape_grass=texture(cape_turf,vec2((paint_position.x+26.0)/15.0,(paint_z+8.4)/12.0)).rgb;
    float outer_corner=1.0-smoothstep(-25.5,-24.15,world_position.x);
    brush=mix(brush,cape_grass,outer_corner*.92);
    vec3 east=texture(east_brush,vec2((world_position.x+1.0)/30.0,(world_position.z+7.0)/14.0)).rgb;
    brush=mix(brush,east,smoothstep(-1.0,2.7,world_position.x));
    // The small cold fire site clears painted grass under ash and perimeter stones.
    // It follows the Blender-authored campfire placement; no terrain is generated.
    vec2 fire_delta=world_position.xz-vec2(-27.35,-2.15);
    vec2 fire_uv=vec2(dot(fire_delta,vec2(.882948,-.469472)),dot(fire_delta,vec2(.469472,.882948)))/1.7;
    float fire_angle=atan(fire_uv.y,fire_uv.x);
    float fire_radius=length(fire_uv/vec2(.73,.62));
    fire_radius+=.035*sin(fire_angle*5.0)+.025*sin(fire_angle*9.0+.6);
    float fire_wash=1.0-smoothstep(.72,1.18,fire_radius);
    vec3 cold_soil=mix(vec3(.080,.085,.067),vec3(.128,.126,.092),smoothstep(.24,.96,fire_radius));
    float ash_wash=1.0-smoothstep(.34,.78,fire_radius+.065*sin(fire_angle*3.0+.8));
    float ash_pool=exp(-dot((fire_uv-vec2(-.16,.11))/vec2(.32,.20),(fire_uv-vec2(-.16,.11))/vec2(.32,.20)));
    cold_soil=mix(cold_soil,mix(vec3(.115,.126,.110),vec3(.21,.22,.187),ash_pool),ash_wash);
    brush=mix(brush,cold_soil,fire_wash*.92);
    // The road-side stones now belong to the forest. Their old painted
    // contact washes are removed instead of leaving dark marks on the path.
    // The west canopy needs real sun/shadow separation at the forest margin.
    float west_grove=smoothstep(-17.5,-14.0,world_position.x)*(1.0-smoothstep(.2,3.0,world_position.x));
    float canopy=west_grove*(1.0-smoothstep(1.4,3.6,world_position.z));
    float grove=forest_extent(world_position);
    ALBEDO=brush*mix(.66,.90,grove);
    EMISSION=brush*mix(.30,.025,grove);
    AO=mix(1.0,.32,grove);
    AO_LIGHT_AFFECT=0.0;
    ROUGHNESS=1.0;
    if(coastal_edge_enabled){
        float edge=clamp(UV2.x,0.0,1.0);
        // glTF flips the second component of the Blender-authored edge channel.
        vec3 mineral=texture(coastal_edge_paint,vec2(1.0-UV2.y,.013)).rgb*vec3(1.12,.97,.93);
        if(world_position.x>-23.0 && world_position.x< -5.0 && world_position.z>1.8){
            mineral=texture(junction_edge_paint,vec2(1.0-UV2.y,0.0)).rgb*vec3(1.12,.97,.93);
            edge=0.0;
        }
        ALBEDO=mix(ALBEDO,mineral,edge);
        EMISSION=mix(EMISSION,mineral*.025,edge);
        AO=mix(AO,1.0,edge);
        vec4 rock_crown=texture(shallow_cape_surface,vec2((world_position.x+32.0)/13.0,(world_position.z+5.5)/11.0));
        float bare=rock_crown.a*(1.0-smoothstep(-22.0,-20.7,world_position.x));
        ALBEDO=mix(ALBEDO,rock_crown.rgb*.95,bare);
        EMISSION=mix(EMISSION,rock_crown.rgb*.14,bare);
        ALBEDO=mix(ALBEDO,cold_soil*.9,fire_wash*.78*bare);
        EMISSION=mix(EMISSION,cold_soil*.12,fire_wash*.78*bare);
        AO=mix(AO,1.0,bare);
    }
}
void light(){
    float mask=LIGHT_IS_DIRECTIONAL ? forest_sun_mask(world_position,TIME) : forest_local_light_mask(world_position);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.0)*mask/PI;
}
