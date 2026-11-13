// Sumiro backdrop-eS84m0Yx.js: original paper and red cloud masks, in a Godot sky.
shader_type sky;
uniform sampler2D paper : filter_linear_mipmap, repeat_enable;
uniform sampler2D sky_mask : filter_linear_mipmap, repeat_disable;
uniform sampler2D sky_bank : filter_linear_mipmap, repeat_disable;
uniform sampler2D far_ranges : filter_linear_mipmap, repeat_enable;
vec3 display_to_scene(vec3 c){
    vec3 y=mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a=2.51-2.43*y,b=.03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}
vec3 redWash(float x){
    vec3 c=vec3(1.0);
    c=mix(c,vec3(.995,.940,.900),smoothstep(.04,.26,x));
    c=mix(c,vec3(.960,.800,.760),smoothstep(.24,.52,x));
    c=mix(c,vec3(.930,.695,.675),smoothstep(.50,.78,x));
    c=mix(c,vec3(.895,.620,.600),smoothstep(.78,1.0,x));
    return c;
}
void sky(){
    vec3 d=normalize(EYEDIR);
    float az=atan(-d.x,-d.z)*57.29578;
    float el=asin(clamp(d.y,-1.0,1.0))*57.29578;
    vec2 puv=vec2(atan(-d.x,-d.z),asin(clamp(d.y,-1.0,1.0)))/(2.0*PI/3.0);
    float g=(texture(paper,vec2(puv.x,1.0-puv.y)).r*255.0-128.0)/640.0;
    vec3 col=vec3(195.8,183.2,152.0)/255.0*(1.0+g*(g<0.0?vec3(.82,1.0,1.34):vec3(1.0)));
    col*=mix(vec3(1.0),vec3(1.022,.988,.948),smoothstep(3.0,18.0,el));
    col*=mix(vec3(1.0),vec3(1.016,1.012,1.040),1.0-smoothstep(-.5,8.0,el));
    vec2 uv=vec2((95.0-az)/180.0,(el+10.0)/50.0);
    uv.x+=TIME*.00012;
    if(uv.x>0.0&&uv.x<1.0&&uv.y>0.0&&uv.y<1.0){
        vec3 m=texture(sky_mask,vec2(uv.x,1.0-uv.y)).rgb;
        float edge=smoothstep(0.0,.04,uv.x)*(1.0-smoothstep(.96,1.0,uv.x))*(1.0-smoothstep(.94,1.0,uv.y));
        float stain=(m.b*255.0-128.0)/8.0*edge;
        col*=1.0+stain*vec3(.0085,.0115,.0165);
        col*=mix(vec3(1.0),vec3(.915,.810,.740),m.g*edge);
        float bank=texture(sky_bank,vec2(uv.x,1.0-uv.y)).r*.2;
        col*=mix(vec3(1.0),redWash(max(m.r,bank)),edge);
    }
    // The original floor paint is replaced by the requested clear sea.
    float v=(el+9.0)/15.0;
    if(v>0.0&&v<1.0){
        vec4 f=texture(far_ranges,vec2(fract((180.0-az)/360.0),1.0-v));
        col=mix(col,f.rgb*(1.0+g*.5),f.a);
    }
    COLOR=display_to_scene(col);
}
