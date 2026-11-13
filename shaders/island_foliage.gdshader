shader_type spatial;
render_mode cull_disabled, diffuse_lambert_wrap, specular_disabled;
uniform sampler2D leaf_texture : source_color, filter_nearest;
uniform float breeze = 0.10;
uniform vec4 tint : source_color = vec4(1.0);
void vertex() {
    vec3 p = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    VERTEX.x += sin(TIME*1.1+p.x*0.85+p.z*0.5) * breeze * (1.0-UV.y);
}
void fragment() {
    vec4 tex = texture(leaf_texture,UV);
    ALBEDO = tex.rgb*tint.rgb;
    ALPHA = tex.a;
    ALPHA_SCISSOR_THRESHOLD = 0.5;
    ROUGHNESS = 1.0;
    NORMAL = normalize(NORMAL + vec3(0.0,0.55,0.0));
	BACKLIGHT = vec3(0.05,0.07,0.02);
}
