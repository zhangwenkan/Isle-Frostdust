shader_type fog;
void fog(){
    vec3 p=WORLD_POSITION;
    float depth=smoothstep(3.2,5.2,-p.z)*(1.0-smoothstep(12.0,14.0,-p.z));
    float right_edge=.9;
    float footprint=smoothstep(-18.2,-14.2,p.x)*(1.0-smoothstep(-4.5,right_edge,p.x));
    float terrace_depth=-p.z+.2*sin(p.x*.4);
    float floor_height=1.7+smoothstep(3.0,4.9,terrace_depth)+2.3*smoothstep(6.0,7.2,terrace_depth)+2.5*smoothstep(7.9,9.5,terrace_depth)+3.2*smoothstep(10.0,12.0,terrace_depth);
    floor_height=1.7+(floor_height-1.7)*footprint;
    float height=smoothstep(floor_height,floor_height+.6,p.y)*(1.0-smoothstep(floor_height+1.8,floor_height+3.4,p.y));
    vec3 q=p+vec3(sin(p.z*.31+TIME*.13)*.7,0.0,sin(p.x*.28-TIME*.11)*.8);
    float pockets=.5+.28*sin(q.x*.46+q.z*.31+TIME*.18)*sin(q.z*.51-q.y*.42-TIME*.10)+.16*sin(q.x*.93+q.z*.37-TIME*.07);
    float banks=exp(-pow((p.z+5.2)/1.3,2.0))*.65+exp(-pow((p.z+8.7)/1.7,2.0))*.8;
    DENSITY=.075*depth*footprint*height*smoothstep(.24,.76,pockets)*banks;
    ALBEDO=vec3(.47,.56,.47);
    EMISSION=vec3(.045,.056,.038)*depth*height*banks*footprint*smoothstep(.24,.76,pockets);
}
