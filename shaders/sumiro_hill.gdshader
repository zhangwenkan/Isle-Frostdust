// Sumiro backdrop painting on the source relief geometry. See assets/sumiro/PROVENANCE.md.
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D painting : filter_linear_mipmap_anisotropic;
uniform sampler2D scene_depth : hint_depth_texture, filter_nearest;
vec3 display_to_scene(vec3 c){
    vec3 y=mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a=2.51-2.43*y,b=.03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}
void fragment(){
    float raw=texture(scene_depth,SCREEN_UV).r;
    vec4 behind=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.0-1.0,raw,1.0);
    if(raw>.00001 && -behind.z/behind.w<55.0)discard;
    vec4 m=texture(painting,UV);
    if(m.a<.008)discard;
    ALBEDO=display_to_scene(m.rgb);
    ALPHA=m.a;
}
