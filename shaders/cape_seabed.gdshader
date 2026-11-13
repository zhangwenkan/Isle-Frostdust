shader_type spatial;
render_mode cull_disabled,diffuse_burley,specular_disabled;
varying vec3 world_position;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    float cape=smoothstep(-40.0,-35.5,world_position.x)*(1.0-smoothstep(-23.0,-17.0,world_position.x))
        *(1.0-smoothstep(7.0,13.0,abs(world_position.z)));
    // The original white substrate only became exposed after lowering the cape.
    // Local mineral color keeps the raised shoal readable through transmission.
    vec3 sand=COLOR.rgb*vec3(.44,.56,.54);
    ALBEDO=mix(vec3(1.0),sand,cape);
    ROUGHNESS=.9;
}
