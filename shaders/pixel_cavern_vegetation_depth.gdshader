shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_always, shadows_disabled;

#include "res://shaders/pixel_cavern_vegetation.gdshaderinc"

void vertex() {
    vec3 point = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    vec3 surface_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
    float t = vegetation_time >= 0.0 ? vegetation_time : TIME;
    vegetation_deform(point, surface_normal, UV, UV2, COLOR, t);
    VERTEX = (inverse(MODEL_MATRIX) * vec4(point, 1.0)).xyz;
}

void fragment() {
    ALBEDO = vec3(0.0);
    ALPHA = 0.0;
}
