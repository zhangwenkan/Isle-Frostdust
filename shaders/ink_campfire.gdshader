shader_type spatial;
render_mode diffuse_burley, specular_disabled;
uniform sampler2D brush_color : source_color, filter_linear_mipmap_anisotropic;
uniform bool use_texture=false;
varying vec3 world_normal;
void vertex(){world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 pigment=COLOR.rgb;
    if(use_texture){pigment*=texture(brush_color,UV).rgb;}
    // Matched pigment fill; this is a cold surface, not a glowing ember effect.
    ALBEDO=pigment*.76;
    EMISSION=pigment*.18;
    ROUGHNESS=1.0;
}
