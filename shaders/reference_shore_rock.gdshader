shader_type spatial;
render_mode diffuse_burley,specular_disabled;
// Local study using original Wandering Sword shore color texture; see SOURCE.json.
uniform sampler2D original_color : source_color,filter_linear_mipmap_anisotropic,repeat_disable;
varying vec3 world_position;
varying vec3 world_normal;
void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;world_normal=normalize((MODEL_MATRIX*vec4(NORMAL,0.0)).xyz);}
void fragment(){
    vec3 stone=pow(max(texture(original_color,UV).rgb,vec3(.0001)),vec3(.72))*.93;
    float value=dot(stone,vec3(.2126,.7152,.0722));
    stone=mix(stone,vec3(value)*vec3(1.04,1.0,.91),.25);
    float turf_edge=smoothstep(1.48,1.82,world_position.y)*smoothstep(.40,.86,world_normal.y);
    stone*=mix(vec3(1.0),vec3(.69,.79,.57),turf_edge*.82);
    ALBEDO=stone;
    EMISSION=stone*.04;
    ROUGHNESS=1.0;
}
