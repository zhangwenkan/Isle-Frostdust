shader_type spatial;
// Transparent depth proxies render before the full-resolution character.
render_mode unshaded, cull_disabled, depth_draw_always, shadows_disabled;
uniform float surface_kind = 0.0;
uniform float wind_amount = 0.0;
void vertex() {
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float anchor=surface_kind>2.5 ? clamp((wp.y-3.13)/.28,0.0,1.0) : clamp((wp.y-3.4)/4.5,0.0,1.0);
    VERTEX.x+=wind_amount*anchor*(sin(TIME*1.5+wp.x*.6+wp.z*.4)*.7+sin(TIME*.7+wp.z)*.3);
}
void fragment() { ALBEDO=vec3(0.0); ALPHA=0.0; }
