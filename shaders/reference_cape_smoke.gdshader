shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never;
uniform float phase=0.0;
void vertex(){float h=1.0-UV.y;VERTEX.x+=(sin(TIME*.38+phase+h*4.0)*.12+h*.38)*h;}
void fragment(){
    float h=1.0-UV.y;
    float x=abs(UV.x-.5-sin(h*6.0-TIME*.5+phase)*.10);
    float body=(1.0-smoothstep(.08,.24+h*.18,x))*smoothstep(0.0,.13,h)*(1.0-smoothstep(.48,1.0,h));
    float clumps=.58+.32*sin(h*21.0-TIME*1.5+sin(UV.x*12.0+phase));
    ALBEDO=vec3(.36,.33,.29);ALPHA=body*clumps*.12;
}
