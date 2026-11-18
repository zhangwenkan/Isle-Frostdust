// One canopy projection drives surfaces, painted forest, mist and light veils.
uniform vec3 forest_ray_direction=vec3(.479,-.789,-.383);
uniform vec4 forest_sun_tint:source_color=vec4(1.0,.87,.65,1.0);
uniform float forest_light_strength=1.0;
uniform float forest_light_time_override=-1.0;
float forest_field_hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float forest_field_noise(vec2 p){
    vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);
    return mix(mix(forest_field_hash(i),forest_field_hash(i+vec2(1,0)),f.x),mix(forest_field_hash(i+vec2(0,1)),forest_field_hash(i+vec2(1,1)),f.x),f.y);
}
vec2 forest_canopy_projection(vec3 p){
    vec3 ray=normalize(forest_ray_direction);
    // Points on one solar ray reach the same opening at the canopy plane.
    return p.xz-ray.xz*((p.y-16.0)/min(ray.y,-.08));
}
float forest_aperture(vec3 p,float time){
    float t=forest_light_time_override>=0.0?forest_light_time_override:time;
    vec2 q=forest_canopy_projection(p);
    vec2 flex=vec2(sin(q.y*.23+t*.37)*.32,cos(q.x*.20-t*.29)*.24);
    float leaf=.30+.70*smoothstep(.19,.80,forest_field_noise(q*.43+flex));
    float cloud=.12+.88*smoothstep(.15,.82,forest_field_noise(q*vec2(.11,.12)+vec2(t*.065,-t*.038)));
    float opening0=exp(-pow((q.x+58.0+sin(q.y*.13)*.9)/5.0,2.0));
    float opening1=exp(-pow((q.x+40.0+sin(q.y*.11+1.3)*1.1)/6.3,2.0));
    float opening2=exp(-pow((q.x+23.0+sin(q.y*.17+2.7)*.7)/4.2,2.0));
    return pow(clamp((opening0*.85+opening1+opening2*.75)*leaf*cloud,0.0,1.0),.72);
}
vec3 forest_painted_light(vec3 color,vec3 p,float t){
    float sun=forest_aperture(p,t);
    vec3 shaded=color*(vec3(.46,.58,.57)+forest_sun_tint.rgb*sun*1.70);
    return mix(color*.955,shaded,forest_light_strength);
}
