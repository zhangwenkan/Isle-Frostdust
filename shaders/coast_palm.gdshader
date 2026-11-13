shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;
uniform sampler2D albedo_texture : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform sampler2D normal_texture : hint_normal, filter_linear_mipmap_anisotropic, repeat_disable;
uniform float wind_strength = 0.05;
varying float canopy;

void vertex() {
    vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    canopy = smoothstep(1.8, 4.2, VERTEX.y);
    float breeze = sin(TIME * 0.85 + world.x * 0.23 + world.z * 0.32);
    VERTEX.x += breeze * canopy * wind_strength;
    VERTEX.z += sin(TIME * 0.7 + world.x * 0.31) * canopy * wind_strength * 0.42;
}
void fragment() {
	if (!FRONT_FACING) { NORMAL = -NORMAL; }
    vec3 pigment = texture(albedo_texture, UV).rgb;
    float value = dot(pigment, vec3(0.2126, 0.7152, 0.0722));
    ALBEDO = mix(vec3(value), pigment, 0.82) * 0.72;
    NORMAL_MAP = texture(normal_texture, UV).rgb;
    NORMAL_MAP_DEPTH = 0.55;
    ROUGHNESS = 0.88;
    SPECULAR = 0.16;
    BACKLIGHT = ALBEDO * canopy * 0.06;
}
