shader_type spatial;
render_mode cull_disabled, specular_disabled;
varying vec3 world;
void vertex() {
    world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    // Authored broad blades bend very gently with the same shoreward current.
    float weight = UV2.x;
    VERTEX.x += sin(TIME * 1.2 + world.z * 0.5) * 0.055 * weight;
    VERTEX.z += cos(TIME * 0.8 + world.x) * 0.025 * weight;
}
void fragment() {
    if (!FRONT_FACING) { NORMAL = -NORMAL; }
    ALBEDO = vec3(0.075,0.22,0.16);
    ROUGHNESS = 1.0;
    BACKLIGHT = ALBEDO * 0.08;
}
