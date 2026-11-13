shader_type spatial;
render_mode unshaded, fog_disabled, cull_disabled, depth_draw_never, depth_test_disabled;

uniform sampler2D scene_color : hint_screen_texture, filter_linear;
uniform sampler2D scene_depth : hint_depth_texture, filter_nearest;
uniform bool enabled = true;
uniform float focus_distance = 19.39;
varying flat mat4 inverse_projection;

void vertex() {
    POSITION = vec4(VERTEX.xy, 1.0, 1.0);
    inverse_projection = INV_PROJECTION_MATRIX;
}
float view_depth(vec2 uv) {
    float d = texture(scene_depth,uv).r;
    // OpenGL Compatibility uses [-1,1] NDC depth, including reverse Z in Godot 4.6.
    #if CURRENT_RENDERER == RENDERER_COMPATIBILITY
    vec3 ndc = vec3(uv,d)*2.0-1.0;
    #else
    vec3 ndc = vec3(uv*2.0-1.0,d);
    #endif
    vec4 v = inverse_projection*vec4(ndc,1.0);
    return -v.z/v.w;
}
void fragment() {
    vec2 uv = SCREEN_UV;
    vec2 px = 1.0/VIEWPORT_SIZE;
    float depth = view_depth(uv);
    float far_amount = smoothstep(focus_distance+4.0,focus_distance+23.0,depth);
    float near_amount = 1.0-smoothstep(focus_distance-8.0,focus_distance-3.8,depth);
    float blur = enabled ? max(far_amount*1.05,near_amount*1.45) : 0.0;
    vec2 heat = enabled ? vec2(sin(uv.y*110.0+TIME*.65)*px.x*.18*far_amount,0.0) : vec2(0.0);
    vec3 center = texture(scene_color,uv+heat).rgb;
    vec3 color = center*.36;
    color += texture(scene_color,uv+heat+px*vec2(blur,0)).rgb*.16;
    color += texture(scene_color,uv+heat-px*vec2(blur,0)).rgb*.16;
    color += texture(scene_color,uv+heat+px*vec2(0,blur)).rgb*.16;
    color += texture(scene_color,uv+heat-px*vec2(0,blur)).rgb*.16;
    if (enabled) {
        vec3 halo = max(texture(scene_color,uv+px*vec2(2,1)).rgb-vec3(.82),vec3(0.0));
        color += halo*.055;
    }
    ALBEDO = color;
}
