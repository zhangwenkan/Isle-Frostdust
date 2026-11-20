shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_always,shadows_disabled;
uniform float kind=0.0;
void vertex(){
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1)).xyz;
}
void fragment(){ALBEDO=vec3(0);ALPHA=0.0;}
