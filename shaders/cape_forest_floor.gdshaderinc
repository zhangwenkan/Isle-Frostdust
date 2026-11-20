// One registered painting spans the rock shelf, mouth and existing forest.
uniform bool continuity_enabled=false;
uniform sampler2D continuity_floor:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform vec4 continuity_bounds=vec4(-74.0,-5.0,24.0,33.0);
float continuity_weight(vec3 p){
    float depth=-p.z;
    vec2 q=(vec2(p.x,depth)-continuity_bounds.xy)/continuity_bounds.zw;
    float bounds=step(0.0,q.x)*step(q.x,1.0)*step(0.0,q.y)*step(q.y,1.0);
    return continuity_enabled?bounds*(1.0-smoothstep(-57.0,-52.5,p.x))*(1.0-smoothstep(24.0,28.0,depth)):0.0;
}
vec3 continuity_color(vec3 original,vec3 p,float upward){
    vec2 uv=(vec2(p.x,-p.z)-continuity_bounds.xy)/continuity_bounds.zw;uv.y=1.0-uv.y;
    float weight=continuity_weight(p)*smoothstep(.45,.78,upward);
    return mix(original,texture(continuity_floor,uv).rgb,weight);
}
