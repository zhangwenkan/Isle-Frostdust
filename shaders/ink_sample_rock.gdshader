shader_type spatial;
render_mode diffuse_burley, specular_disabled;
uniform sampler2D brush_color : source_color, filter_linear_mipmap_anisotropic;
varying vec3 stone_world_normal;
void vertex(){
    stone_world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 pigment=texture(brush_color,UV).rgb;
    // Plane readability comes from light and sparse brushwork. A view-angle
    // dark rim on flat faces made each plane look like a plastic panel.
    // A broad upper-left sky fill keeps shadowed planes readable in the grove.
    // It uses a common world-space direction, independent of UV tile or view.
    float sky_fill=max(dot(normalize(stone_world_normal),normalize(vec3(-.65,.70,.45))),0.0);
    ALBEDO=pigment*.82;
    EMISSION=pigment*(.075+.22*sky_fill);
    ROUGHNESS=1.0;
}
