shader_type spatial;
render_mode unshaded,blend_add,cull_disabled,depth_draw_never,fog_disabled,shadows_disabled;
uniform float phase=0.0;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    float edge=pow(max(0.0,1.0-abs(UV.x-.5)*2.0),2.3);
    float ends=smoothstep(.0,.18,UV.y)*(1.0-smoothstep(.73,1.0,UV.y));
    float drift=sin(UV.y*8.0+TIME*.28+phase)*.09+sin(UV.y*19.0-TIME*.17+phase)*.035;
    float strands=.52+.32*sin((UV.x+drift)*17.0+phase)+.16*sin(UV.x*34.0-UV.y*6.0+TIME*.22);
    float breathe=.75+.25*sin(TIME*.23+phase);
    ALBEDO=vec3(.78,.84,.64);
    ALPHA=edge*ends*strands*breathe*.20;
}
