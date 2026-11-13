// Analytic volumetric cloud field: no cloud images, planes or baked animation.
// World position supplies parallax; evolving domain warps supply local deformation.
float pc_hash(vec3 p){
    p=fract(p*.1031);
    p+=dot(p,p.yzx+33.33);
    return fract((p.x+p.y)*p.z);
}
float pc_noise(vec3 p){
    vec3 i=floor(p),f=fract(p);
    f=f*f*f*(f*(f*6.0-15.0)+10.0);
    return mix(mix(mix(pc_hash(i),pc_hash(i+vec3(1,0,0)),f.x),
        mix(pc_hash(i+vec3(0,1,0)),pc_hash(i+vec3(1,1,0)),f.x),f.y),
        mix(mix(pc_hash(i+vec3(0,0,1)),pc_hash(i+vec3(1,0,1)),f.x),
        mix(pc_hash(i+vec3(0,1,1)),pc_hash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
float pc_body(vec3 p){
    return pc_noise(p)*.57+pc_noise(p*2.07+vec3(7.1,3.7,-2.3))*.29
        +pc_noise(p*4.19+vec3(-1.3,11.2,5.4))*.14;
}
vec3 pc_display_to_scene(vec3 c){
    vec3 y=mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
    vec3 a=2.51-2.43*y,b=.03-.59*y;
    return max((-b+sqrt(b*b+4.0*a*.14*y))/(2.0*a),vec3(0.0));
}
float pc_density(vec3 point,float seconds,float cover){
    float high_layer=smoothstep(285.0,390.0,point.y);
    vec3 wind=vec3(-2.1,0.0,-.63)*seconds*mix(1.0,.48,high_layer);
    vec3 p=point+wind;
    vec3 warp_coord=p*vec3(.0019,.005,.0019);
    vec3 warp=vec3(
        pc_noise(warp_coord+vec3(0,seconds*.032,0)),
        pc_noise(warp_coord+vec3(11.2,0,seconds*.023)),
        pc_noise(warp_coord+vec3(seconds*.019,7.9,2.3)))-.5;
    float weather=pc_noise(vec3(p.x*.00135,seconds*.012,p.z*.00135));
    float floor_height=55.0+warp.y*42.0;
    // Bank tops rise locally, instead of cutting every cloud at one flat altitude.
    float top_height=145.0+weather*245.0+warp.x*70.0;
    float layer=smoothstep(floor_height,floor_height+45.0,point.y)
        *(1.0-smoothstep(top_height-65.0,top_height,point.y));
    float upper=smoothstep(355.0,390.0,point.y)*(1.0-smoothstep(455.0,510.0,point.y));
    vec3 q=p*vec3(.0032,.0048,.0036)+warp*1.45;
    q.y+=seconds*.016;
    float body=pc_body(q);
    float threshold=mix(.58,.36,cover)+(.5-weather)*.16;
    float density=smoothstep(threshold,threshold+.20,body);
    float banks=smoothstep(.34,.59,weather);
    // The higher veil has its own gaps and moves more slowly than the main banks.
    float high_banks=smoothstep(.38,.65,pc_noise(p*vec3(.0021,0.0,.0021)+vec3(17.3,seconds*.008,9.2)));
    return density*(layer*banks+upper*high_banks*.25);
}
vec4 pc_clouds(vec3 ray,vec3 eye,float seconds,float cover,bool sunset){
    if(ray.y<.006)return vec4(0.0);
    float start=max(180.0,(35.0-eye.y)/max(ray.y,.012));
    float finish=min(3100.0,(515.0-eye.y)/max(ray.y,.012));
    if(start>=finish)return vec4(0.0);
    float step_size=(finish-start)/24.0;
    vec3 light_dir=normalize(sunset?vec3(-.25,.24,-.94):vec3(-.3,.65,-.7));
    vec3 shaded=sunset?vec3(.59,.61,.60):vec3(.55,.66,.71);
    vec3 lit=sunset?vec3(.84,.786,.674):vec3(.91,.93,.89);
    vec3 horizon=sunset?vec3(.745,.749,.718):vec3(.77,.83,.83);
    vec3 color=vec3(0.0);
    float transmittance=1.0;
    for(int i=0;i<24;i++){
        float distance=start+(float(i)+.5)*step_size;
        vec3 p=eye+ray*distance;
        float density=pc_density(p,seconds,cover);
        if(density>.002){
            float sunlight=exp(-pc_density(p+light_dir*75.0,seconds,cover)*2.7);
            float lighting=clamp(.24+sunlight*.60+smoothstep(65.0,210.0,p.y)*.16,0.0,1.0);
            vec3 pigment=mix(shaded,lit,lighting);
            pigment=mix(pigment,horizon,smoothstep(1000.0,3100.0,distance)*.42);
            float alpha=1.0-exp(-density*step_size*.0032);
            color+=transmittance*alpha*pc_display_to_scene(pigment);
            transmittance*=1.0-alpha;
            if(transmittance<.015)break;
        }
    }
    float alpha=(1.0-transmittance)*smoothstep(.008,.045,ray.y);
    return vec4(color/max(1.0-transmittance,.001),alpha);
}
vec3 pc_sky_base(vec3 ray,vec3 top,vec3 horizon,vec3 ground,vec3 ground_horizon,float upper_curve,float lower_curve){
    float elevation=asin(clamp(ray.y,-1.0,1.0))/(PI*.5);
    return ray.y>=0.0?mix(horizon,top,pow(max(elevation,0.0),upper_curve))
        :mix(ground_horizon,ground,pow(max(-elevation,0.0),lower_curve));
}
