shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;
uniform vec3 haze_color : source_color = vec3(0.62, 0.75, 0.77);
varying float mountain_distance;
varying vec3 mountain_world;
void vertex() {
    mountain_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    mountain_distance = -mountain_world.z;
}
void fragment() {
    float aerial = mix(0.12, 0.55, smoothstep(65.0, 190.0, mountain_distance));
    ALBEDO = COLOR.rgb * (1.0 - aerial);
    EMISSION = haze_color * aerial * 0.55;
    ROUGHNESS = 1.0;
}
