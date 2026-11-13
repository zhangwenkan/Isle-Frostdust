shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform sampler2D ground_atlas : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
varying vec3 world_position;
varying float blade_tip;
#include "res://shaders/coastal_wind.gdshaderinc"

void vertex() {
    world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    blade_tip = smoothstep(0.21, 0.30, COLOR.g);
    VERTEX.xz += coastal_bend(world_position, TIME) * 0.075 * blade_tip;
    VERTEX.x += sin(TIME * 2.2 + world_position.x * 0.8) * 0.01 * blade_tip;
    // Bent grass receives sky illumination similarly to the surrounding turf.
    NORMAL = normalize(mix(NORMAL, vec3(0.0, 1.0, 0.0), 0.72));
}
void fragment() {
    vec2 ground_uv = vec2((world_position.x + 20.0) / 48.0, (world_position.z + 7.0) / 12.0);
    vec3 ground = texture(ground_atlas, ground_uv).rgb;
    ALBEDO = ground * vec3(0.57, 0.64, 0.59) * mix(0.86, 1.08, blade_tip);
    ROUGHNESS = 1.0;
    BACKLIGHT = ALBEDO * 0.04;
}
