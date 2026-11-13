shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D brush_color : source_color, filter_linear_mipmap_anisotropic;
uniform bool is_rope=false;
uniform bool is_end=false;
uniform bool is_binding=false;
varying vec3 world_normal;
void vertex(){world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 pigment=texture(brush_color,UV).rgb;
    // Dilute sparse long-axis strokes without the former sparkling wood grooves
    // or view-dependent dark outlines. Shape and the scene sun carry the volume.
    if(is_end) pigment*=.91;
    float sky_fill=max(dot(normalize(world_normal),normalize(vec3(-.65,.70,.45))),0.0);
    ALBEDO=pigment*(is_rope?.78:.82);
    EMISSION=pigment*(is_rope?(is_binding?.21:.115):(.065+.14*sky_fill));
    ROUGHNESS=1.0;
}
