shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_disabled;

uniform sampler2D albedo_texture : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform vec4 base_color : source_color = vec4(1.0);
uniform float amplitude = 0.045;
uniform bool is_grass = false;

void vertex() {
    vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    float anchored_height = is_grass ? clamp(VERTEX.y / 0.4, 0.0, 1.0) : smoothstep(1.0, 5.3, VERTEX.y);
    float breeze = sin(TIME * 1.05 + world.x * 0.39 + world.z * 0.24);
    VERTEX.x += breeze * amplitude * anchored_height;
    VERTEX.z += cos(TIME * 0.83 + world.x * 0.27) * amplitude * 0.35 * anchored_height;
}

void fragment() {
    vec4 source = texture(albedo_texture, UV);
    ALBEDO = source.rgb * base_color.rgb;
    ALPHA = source.a;
    ALPHA_SCISSOR_THRESHOLD = 0.5;
    ROUGHNESS = 1.0;
    BACKLIGHT = ALBEDO * 0.22;
}
