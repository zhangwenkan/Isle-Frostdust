shader_type sky;
void sky(){
    float h=clamp(EYEDIR.y,0.0,1.0);
    vec3 horizon=vec3(.72,.75,.70);vec3 high=vec3(.72,.61,.59);
    vec3 col=mix(horizon,high,smoothstep(.0,.42,h));
    float warm=pow(max(0.0,1.0-length(EYEDIR.xz-vec2(-.48,-.70))*.75),5.0);
    col+=vec3(.20,.10,.045)*warm;
    vec2 p=EYEDIR.xz/max(.16,EYEDIR.y+.22);
    float cloud=sin(p.x*.85+TIME*.006+sin(p.y*.60))*sin(p.y*1.8-TIME*.005)+.32*sin(p.x*2.0-p.y*1.3);
    float c=smoothstep(.30,.90,cloud)*smoothstep(.03,.18,h)*(1.0-smoothstep(.8,1.0,h));
    COLOR=mix(col,col+vec3(.075,.065,.045),c*.6);
}
