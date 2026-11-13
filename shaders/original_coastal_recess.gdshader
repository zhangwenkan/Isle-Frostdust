shader_type spatial;
render_mode diffuse_burley,specular_disabled;
// The continuous earth/rock core closes gaps behind the authored coastal modules.
varying float world_height;
void vertex(){world_height=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;}
void fragment(){
    float turf=smoothstep(1.50,1.87,world_height);
    vec3 pigment=mix(vec3(.245,.164,.112),vec3(.135,.160,.087),turf*.65);
    ALBEDO=pigment;
    EMISSION=pigment*.025;
    ROUGHNESS=1.0;
}
