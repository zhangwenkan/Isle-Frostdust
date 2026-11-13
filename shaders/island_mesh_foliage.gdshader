shader_type spatial;
render_mode cull_disabled, diffuse_lambert, specular_disabled;

uniform vec4 base_color : source_color = vec4(0.2,0.4,0.15,1.0);
uniform sampler2D albedo_texture : source_color, filter_nearest, repeat_disable;
uniform bool use_texture = false;
uniform float amplitude = 0.025;
void vertex() {
    vec3 world = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz;
    float height_weight = smoothstep(0.0,6.0,world.y);
    VERTEX.x += sin(TIME*1.25+world.x*0.7+world.z)*amplitude*height_weight;
}
void fragment() {
    vec4 tex = use_texture ? texture(albedo_texture, UV) : vec4(1.0);
    ALBEDO = base_color.rgb * tex.rgb;
    ALPHA = tex.a;
    ALPHA_SCISSOR_THRESHOLD = 0.5;
    ROUGHNESS = 1.0;
    BACKLIGHT = ALBEDO*0.12;
    // Painted leaf planes retain their dark underside and catch a little noon sky.
    if (use_texture) {
        NORMAL = normalize(NORMAL + vec3(0.0, 0.4, 0.0));
    }
}
