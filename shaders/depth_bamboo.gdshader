shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform bool is_leaf = false;
#include "res://shaders/coastal_wind.gdshaderinc"
varying vec3 world_position;
void vertex() {
    world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    float height_weight = pow(clamp(UV2.x, 0.0, 1.0), 1.65);
    vec2 bend = coastal_bend(world_position, TIME) * height_weight * 0.37;
    VERTEX.xz += bend;
    VERTEX.y -= dot(bend, bend) * 0.14;
    if (is_leaf) {
        float flutter = sin(TIME * 3.1 + world_position.x * 2.3 + world_position.z * 1.7);
        VERTEX.y += flutter * 0.026 * height_weight * coastal_gust(world_position, TIME);
    }
}
void fragment() {
    if (!FRONT_FACING) { NORMAL = -NORMAL; }
    ALBEDO = COLOR.rgb;
    ROUGHNESS = 0.95;
    BACKLIGHT = ALBEDO * (is_leaf ? 0.20 : 0.0);
}
