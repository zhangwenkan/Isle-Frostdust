// Coordinates stay attached to the authored beach: x runs along shore, y is
// signed distance toward the sea. Only the water pattern changes with time.
float swash_hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);}
float swash_noise(vec2 p){
    vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
    return mix(mix(swash_hash(i),swash_hash(i+vec2(1,0)),f.x),mix(swash_hash(i+vec2(0,1)),swash_hash(i+vec2(1,1)),f.x),f.y);
}
uniform float shoreline_time_override=-1.0;
float shoreline_time(){return shoreline_time_override<0.0?TIME:shoreline_time_override;}
float swash_phase(float s){return fract(shoreline_time()/7.4-s*.009+.028*sin(s*.78));}
float swash_front(float s){
    float phase=swash_phase(s);
    float surge=smoothstep(.015,.28,phase)*(1.0-smoothstep(.34,.96,phase));
    float broken=.15*sin(s*.86+shoreline_time()*.24)+.055*sin(s*5.1-shoreline_time()*.13);
    return .46-1.14*surge+broken;
}
float swash_wetness(vec2 p){
    float phase=swash_phase(p.x);
    // Smooth periodic lag avoids a wetness jump at the cycle boundary.
    float last_front=-.69-.19*cos((phase-.40)*6.2831853);
    float persistent=.78*smoothstep(-1.04,-.23,p.y);
    return max(persistent,smoothstep(last_front-.18,last_front+.17,p.y));
}
