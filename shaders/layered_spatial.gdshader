shader_type spatial;
render_mode cull_disabled, diffuse_burley;
uniform sampler2D painting : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D path_painting : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
uniform bool use_texture = true;
uniform bool cutout = false;
uniform bool ground_path = false;
uniform float wind_strength = 0.0;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 world_position;
float path_segment(vec2 p,vec2 a,vec2 b){
    vec2 v=b-a;
    return length(p-a-v*clamp(dot(p-a,v)/dot(v,v),0.0,1.0));
}
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float gust=sin(TIME*.62+world_position.x*.43+world_position.z*.23)*.6;
    gust+=sin(TIME*1.07+world_position.x*.81)*.23;
    VERTEX.x+=gust*UV2.x*wind_strength;
    VERTEX.z+=sin(TIME*.71+world_position.x*.4)*UV2.x*wind_strength*.27;
}
void fragment(){
    vec4 c=use_texture?texture(painting,UV):vec4(1.0);
    if(ground_path){
        vec2 p=(author_world_to_local*vec4(world_position,1.0)).xz;
        float distance=path_segment(p,vec2(-4.728,.180),vec2(-3.562,-.925));
        distance=min(distance,path_segment(p,vec2(-3.562,-.925),vec2(.236,-1.416)));
        distance=min(distance,path_segment(p,vec2(-3.562,-.925),vec2(-4.307,-2.692)));
        distance=min(distance,path_segment(p,vec2(-4.307,-2.692),vec2(-5.232,-3.942)));
        float edge=.05*sin(p.x*7.1+p.y*4.7)+.035*sin(p.x*3.9-p.y*6.2);
        float path=1.0-smoothstep(.36,.68,distance+edge);
        c.rgb=mix(c.rgb,texture(path_painting,world_position.xz*.27).rgb,path*.92);
    }
    ALBEDO=c.rgb*tint.rgb;
    ROUGHNESS=.98;SPECULAR=.06;
    if(cutout){ALPHA=c.a;ALPHA_SCISSOR_THRESHOLD=.32;}
}
