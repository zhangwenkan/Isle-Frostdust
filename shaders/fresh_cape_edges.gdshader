shader_type spatial;
render_mode unshaded, fog_disabled, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D screen_tex : hint_screen_texture, repeat_disable, filter_nearest;
uniform sampler2D depth_tex : hint_depth_texture, repeat_disable, filter_nearest;
uniform sampler2D normal_tex : hint_normal_roughness_texture, repeat_disable, filter_nearest;

void vertex(){POSITION=vec4(VERTEX.xy,1.0,1.0);}
float view_z(vec2 uv,mat4 inverse_projection){
    float d=texture(depth_tex,uv).r;
    vec4 p=inverse_projection*vec4(uv*2.0-1.0,d,1.0);
    return -p.z/p.w;
}
void fragment(){
    vec2 uv=SCREEN_UV;vec2 px=1.0/VIEWPORT_SIZE;
    vec3 color=texture(screen_tex,uv).rgb;
    vec3 normal=texture(normal_tex,uv).rgb*2.0-1.0;
    float z=view_z(uv,INV_PROJECTION_MATRIX);
    float gap=0.0;float ridge=0.0;
    float material_mask=step(texture(normal_tex,uv).a,.87);
    vec2 offsets[4]=vec2[](vec2(1,0),vec2(-1,0),vec2(0,1),vec2(0,-1));
    for(int i=0;i<4;i++){
        vec2 q=uv+offsets[i]*px;
        float nz=view_z(q,INV_PROJECTION_MATRIX);
        vec3 nn=texture(normal_tex,q).rgb*2.0-1.0;
        gap=max(gap,smoothstep(.12,.25,nz-z)*step(nz-z,3.5));
        float convex=dot(normal-nn,vec3(offsets[i].x,-offsets[i].y,0));
        ridge=max(ridge,step(.16,1.0-dot(normal,nn))*step(.04,convex)*step(abs(nz-z),.20));
    }
    color=mix(color,color*vec3(.70,.79,.84),gap*.48*material_mask);
    color=mix(color,min(vec3(1),color*1.11+vec3(.02,.025,.02)),ridge*.48*material_mask);
    ALBEDO=color;
}
