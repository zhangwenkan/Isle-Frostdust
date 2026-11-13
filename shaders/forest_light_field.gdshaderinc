float forest_extent(vec3 p){return smoothstep(-17.8,-13.8,p.x)*(1.0-smoothstep(.8,4.0,p.x));}
float forest_light_window(vec3 p,float t){
    float depth=max(0.0,-p.z);
    float passage=1.0-smoothstep(.8,2.8,abs(p.z-.25));
    float back_light=exp(-pow((depth-5.2)/2.0,2.0))*.90+exp(-pow((depth-8.5)/1.8,2.0))*.72;
    float large=.68+.20*sin(p.x*.64+p.z*.24+sin(t*.11)*.28)+.12*sin(p.x*1.13-p.z*.34-t*.025);
    return clamp((passage*.92+back_light)*large,0.0,1.0);
}
float forest_sun_mask(vec3 p,float t){
    float pattern=.79+.13*sin(p.x*1.4+p.z*.7+sin(t*.13+p.x*.1)*.6)+.08*sin(p.x*2.8-p.z*.9-t*.06);
    float region=forest_extent(p);
    float shade=mix(.29,1.0,forest_light_window(p,t))*pattern;
    return mix(1.0,shade,region);
}
float forest_local_light_mask(vec3 p){return mix(1.0,1.0-smoothstep(1.0,3.6,p.z)*.92,forest_extent(p));}
