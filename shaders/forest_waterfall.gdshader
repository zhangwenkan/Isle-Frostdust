shader_type spatial;
render_mode blend_mix,depth_draw_opaque,cull_disabled,diffuse_burley,specular_disabled;
uniform bool is_foam=false;

float folded(vec2 p){
    return sin(p.x*3.1+sin(p.y*2.3))*.50+sin(p.x*5.3-p.y*4.7)*.28+sin(p.x*9.7+p.y*8.1)*.22;
}
void vertex(){
    if(!is_foam){
        VERTEX.z+=sin(UV.x*19.0+UV.y*8.0-TIME*4.1)*.012*sin(UV.y*3.14159);
    }
}
void fragment(){
    if(is_foam){
        vec2 p=(UV-.5)*2.0;
        float r=length(p);
        float f=folded(p*4.3+vec2(TIME*.33,-TIME*.21));
        float spreading=sin(r*22.0-TIME*4.8+f*2.8);
        float fleck=smoothstep(-.1,.6,f*.65+spreading*.35);
        float edge=1.0-smoothstep(.38,.94+f*.06,r);
        ALBEDO=mix(vec3(.15,.30,.25),vec3(.55,.67,.59),fleck);
        EMISSION=ALBEDO*.08;
        ALPHA=edge*(.12+fleck*.50);
    }else{
        float t=UV.y;
        float flow=t*(1.0+t*.7)-TIME*.90;
        float strands=sin(UV.x*37.0+sin(flow*9.0+UV.x*11.0)*1.35);
        float broken=folded(vec2(UV.x*9.0,flow*8.0));
        float aeration=smoothstep(.10,.65,t)*.70;
        float white=smoothstep(-.65,.80,strands*.25+broken*.65+aeration*.50);
        float margin=smoothstep(0,.06,UV.x)*(1.0-smoothstep(.94,1.0,UV.x));
        ALBEDO=mix(vec3(.14,.29,.23),vec3(.53,.66,.58),white);
        EMISSION=ALBEDO*.06;
        ALPHA=margin*(.68+white*.23)*(1.0-smoothstep(.94,1.0,t)*.38);
    }
    ROUGHNESS=.48;
}
