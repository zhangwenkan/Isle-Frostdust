shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
uniform sampler2D screen_color:hint_screen_texture,filter_linear_mipmap,repeat_disable;
uniform sampler2D screen_depth:hint_depth_texture,filter_nearest,repeat_disable;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
float wave(vec2 q,float t){
    float drift=q.x-t*(.65+.30*sin(q.y*3.14159));
    return sin(drift*3.4+q.y*8.0+sin(drift*.72+t*.23)*.65)*.52
        +sin(drift*6.2-q.y*14.0+sin(q.y*9.0+t*.37))*.23
        +sin(drift*1.3+q.y*4.0+t*.18)*.25;
}
void fragment(){
    vec2 q=UV;
    float w=wave(q,TIME);
    float slope_x=(wave(q+vec2(.025,0),TIME)-w)*.38;
    float slope_z=(wave(q+vec2(0,.012),TIME)-w)*.16;
    vec3 surface_n=normalize((INV_VIEW_MATRIX*vec4(NORMAL,0.0)).xyz);
    vec3 world_n=normalize(surface_n+vec3(slope_x,0.0,slope_z));
    NORMAL=normalize((VIEW_MATRIX*vec4(world_n,0.0)).xyz);
    float edge=min(q.y,1.0-q.y);
    float raw=texture(screen_depth,SCREEN_UV).r;
    vec4 p=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.0-1.0,raw,1.0);p/=p.w;
    vec3 world_bottom=(INV_VIEW_MATRIX*p).xyz;
    float depth=clamp(world_position.y-world_bottom.y,0.0,3.0);
    vec2 offset=(VIEW_MATRIX*vec4(slope_x,0,slope_z,0)).xy*.008*smoothstep(.01,.3,depth);
    vec2 sample_uv=clamp(SCREEN_UV+offset,vec2(.001),vec2(.999));
    vec4 refracted=INV_PROJECTION_MATRIX*vec4(sample_uv*2.0-1.0,texture(screen_depth,sample_uv).r,1);
    if(refracted.z/refracted.w>VERTEX.z)sample_uv=SCREEN_UV;
    vec3 bottom=textureLod(screen_color,sample_uv,0.0).rgb;
    float fresnel=.025+.20*pow(1.0-clamp(dot(NORMAL,VIEW),0.0,1.0),4.0);
    vec3 transmission=exp(-vec3(2.4,1.4,1.9)*depth)*.58;
    vec3 green=mix(vec3(.032,.120,.083),vec3(.014,.065,.048),smoothstep(.15,.85,depth));
    float bank_ripple=(1.0-smoothstep(.02,.13,edge))*smoothstep(.45,.80,w)*.055;
    ALBEDO=green*(vec3(1.0)-transmission)*(1.0-fresnel);
    float current_ribbon=pow(max(0.0,sin(q.y*31.0+sin(q.x*.7-TIME*.45)*2.2+w*.7)),12.0)
        *smoothstep(.45,.85,sin(q.x*3.3-TIME*1.9+q.y*3.0))*smoothstep(.02,.12,edge);
    ALBEDO+=vec3(.09,.17,.13)*(bank_ripple+current_ribbon*.38);
    EMISSION=bottom*transmission*(1.0-fresnel)+vec3(.13,.22,.19)*fresnel*.18;
    ROUGHNESS=.34;
    SPECULAR=.15;
    RADIANCE=vec4(0,0,0,1);
}
