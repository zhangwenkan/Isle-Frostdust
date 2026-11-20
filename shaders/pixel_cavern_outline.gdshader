shader_type spatial;
render_mode unshaded,fog_disabled,cull_disabled,depth_draw_never,depth_test_disabled;
uniform sampler2D screen_color:hint_screen_texture,repeat_disable,filter_nearest;
uniform sampler2D scene_depth:hint_depth_texture,repeat_disable,filter_nearest;
uniform sampler2D normals:hint_normal_roughness_texture,repeat_disable,filter_nearest;
void vertex(){POSITION=vec4(VERTEX.xy,1,1);}
float distance_at(vec2 uv,mat4 inv_projection){vec4 p=inv_projection*vec4(uv*2.0-1.0,texture(scene_depth,uv).r,1);return -p.z/p.w;}
void fragment(){
    vec2 px=1.0/VIEWPORT_SIZE;vec2 uv=SCREEN_UV;vec3 col=texture(screen_color,uv).rgb;
    vec3 n=texture(normals,uv).xyz*2.0-1.0;float z=distance_at(uv,INV_PROJECTION_MATRIX);
    float mask=step(texture(normals,uv).a,.86);float edge=0.0;float bright=0.0;
    vec2 offsets[4]=vec2[](vec2(1,0),vec2(-1,0),vec2(0,1),vec2(0,-1));
    for(int i=0;i<4;i++){
        vec2 q=uv+offsets[i]*px;float nz=distance_at(q,INV_PROJECTION_MATRIX);vec3 nn=texture(normals,q).xyz*2.0-1.0;
        edge=max(edge,smoothstep(.10,.24,nz-z)*step(nz-z,3.5));
        float facing=dot(n-nn,vec3(offsets[i].x,-offsets[i].y,0));
        bright=max(bright,step(.22,1.0-dot(n,nn))*step(.10,facing)*step(abs(nz-z),.20));
    }
    vec4 vp=INV_PROJECTION_MATRIX*vec4(uv*2.0-1.0,texture(scene_depth,uv).r,1);
    vec3 wp=(INV_VIEW_MATRIX*vec4(vp.xyz/vp.w,1)).xyz;
    mask*=step(.07,wp.y);
    vec3 ink=col*vec3(.62,.74,.79);
    vec3 rim=min(col*1.16+vec3(.022,.024,.017),vec3(1));
    ALBEDO=mix(ink,rim,bright*(1.0-edge));
    ALPHA=clamp(max(edge,bright)*mask*.64,0.0,1.0);
}
