shader_type canvas_item;
render_mode unshaded;
uniform sampler2D screen_texture : hint_screen_texture, filter_nearest;
uniform bool enabled = true;
void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 px = SCREEN_PIXEL_SIZE;
    float far_blur = 1.0-smoothstep(0.12,0.32,uv.y);
	float near_blur = smoothstep(0.73,1.0,uv.y);
    float blur = enabled ? max(far_blur*0.75,near_blur*1.4) : 0.0;
    vec2 heat = enabled ? vec2(sin(uv.y*160.0+TIME*0.8)*px.x*far_blur*0.45,0) : vec2(0);
    vec3 c = texture(screen_texture,uv+heat).rgb*0.40;
    c += texture(screen_texture,uv+heat+px*vec2(blur,0)).rgb*0.15;
    c += texture(screen_texture,uv+heat-px*vec2(blur,0)).rgb*0.15;
    c += texture(screen_texture,uv+heat+px*vec2(0,blur)).rgb*0.15;
    c += texture(screen_texture,uv+heat-px*vec2(0,blur)).rgb*0.15;
    vec3 bloom = max(texture(screen_texture,uv+px*vec2(2,1)).rgb-0.78,vec3(0.0));
    c += enabled ? bloom*0.10 : vec3(0);
    float vignette = smoothstep(0.38,0.76,length((uv-0.5)*vec2(0.85,1.0)));
    c *= 1.0-vignette*0.10;
    COLOR = vec4(c,1.0);
}
