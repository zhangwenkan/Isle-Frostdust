shader_type spatial;
render_mode unshaded, cull_disabled;
uniform sampler2D painting : source_color, filter_linear_mipmap, repeat_disable;
uniform vec4 tint : source_color = vec4(1.0);
uniform float wind_strength = 0.0;
uniform float alpha_cut = 0.30;
uniform float shade_motion = 0.0;
uniform bool project_from_author_camera = false;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 world_position;
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float gust=sin(TIME*.62+world_position.x*.43+world_position.z*.23)*.6;
    gust+=sin(TIME*1.07+world_position.x*.81)*.23;
    VERTEX.x+=gust*UV2.x*wind_strength;
    VERTEX.z+=sin(TIME*.71+world_position.x*.4)*UV2.x*wind_strength*.27;
}
void fragment(){
    vec2 paint_uv=UV;
    if(project_from_author_camera){
        vec3 forward=normalize(vec3(0.0,-21.0,-36.0));
        vec3 up=normalize(cross(vec3(1.0,0.0,0.0),forward));
        vec3 q=(author_world_to_local*vec4(world_position,1.0)).xyz-vec3(0.0,24.0,32.0);
        float depth=dot(q,forward);
        float half_angle=tan(radians(16.0));
        paint_uv=vec2(.5+q.x/(depth*2.0*half_angle*4.0/3.0),.5-dot(q,up)/(depth*2.0*half_angle));
    }
    vec4 c=texture(painting,paint_uv);
    float shade=1.0-shade_motion*(.5+.5*sin(world_position.x*.72+world_position.z*.28-TIME*.17));
    ALBEDO=c.rgb*tint.rgb*shade;
    ALPHA=c.a*tint.a;
    ALPHA_SCISSOR_THRESHOLD=alpha_cut;
}
