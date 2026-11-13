shader_type spatial;
render_mode cull_disabled, specular_disabled;
void vertex() {
    vec3 world = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
    float weight = UV2.x * UV2.x;
    VERTEX.x += sin(TIME * 1.05 + world.x * 0.52) * 0.018 * weight;
    VERTEX.y += sin(TIME * 0.72 + world.x * 0.37) * 0.012 * weight;
}
void fragment() {
    if (!FRONT_FACING) { NORMAL = -NORMAL; }
    ALBEDO = COLOR.rgb;
    ROUGHNESS = 1.0;
    BACKLIGHT = ALBEDO * 0.10;
}
