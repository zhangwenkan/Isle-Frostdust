shader_type spatial;
render_mode diffuse_burley,specular_disabled;
uniform sampler2D mineral_paint : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform sampler2D contact_shading : filter_linear_mipmap,repeat_disable;
uniform sampler2D brush_color : source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D cape_turf : source_color,filter_linear_mipmap_anisotropic;
uniform sampler2D east_brush : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
varying vec3 world_position;
#include "res://shaders/junction_turf.gdshaderinc"
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec4 paint=texture(mineral_paint,UV);
    vec3 pigment=paint.rgb*vec3(1.12,.97,.93);
    float contact=mix(.38,1.0,texture(contact_shading,UV2).r);
    float wet=1.0-smoothstep(-.45,.18,world_position.y);
    vec3 grass=edge_turf(world_position);float grove=forest_extent(world_position);
    ALBEDO=mix(pigment*mix(1.0,.83,wet)*mix(.76,1.0,contact),grass*mix(.66,.90,grove),paint.a);
    EMISSION=mix(pigment*.025*contact,grass*mix(.30,.025,grove),paint.a);
    AO=mix(contact,mix(1.0,.32,grove),paint.a); AO_LIGHT_AFFECT=.40*(1.0-paint.a); ROUGHNESS=1.0;
}
