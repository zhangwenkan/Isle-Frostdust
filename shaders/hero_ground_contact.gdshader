shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
uniform float strength=.25;
uniform float sole_contact=0.0;
void fragment(){
    float radius=length((UV-.5)*2.0);
    ALBEDO=vec3(.035,.055,.043);
    float broad=1.0-smoothstep(.10,1.0,radius);
    float sole=exp(-dot((UV-.5)*vec2(5.0,9.0),(UV-.5)*vec2(5.0,9.0)));
    ALPHA=strength*broad+sole_contact*sole;
}
