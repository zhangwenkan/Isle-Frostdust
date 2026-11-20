shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never,blend_add;
uniform float phase=0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void vertex(){float h=1.0-UV.y;VERTEX.x+=sin(TIME*2.2+phase+h*3.0)*h*h*.075;}
void fragment(){
    float h=1.0-UV.y;
    float n=noise(vec2(UV.x*4.8+phase,h*5.0-TIME*2.6));
    float center=.5+sin(h*5.0+TIME*2.7+phase)*.05*h;
    float width=(.29+.10*n)*pow(max(.0,1.0-h),.74);
    float body=(1.0-smoothstep(width*.48,width,abs(UV.x-center)))*(1.0-smoothstep(.69,.99,h+.065*n));
    float core=(1.0-smoothstep(width*.05,width*.66,abs(UV.x-center)))*(1.0-h);
    vec3 col=mix(vec3(1.0,.18,.013),vec3(1.0,.81,.23),core);
    ALBEDO=col;EMISSION=col*1.4;ALPHA=body*.63;
}
