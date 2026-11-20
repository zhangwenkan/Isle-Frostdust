shader_type spatial;
render_mode diffuse_lambert, specular_disabled, cull_disabled;
#include "res://shaders/pixel_cavern_plant_color.gdshaderinc"
uniform vec4 base_color : source_color = vec4(.5,.6,.4,1);
uniform float kind=0.0;
uniform bool depth_only=false;
varying vec3 world_point;
varying vec3 authored_normal;
void vertex(){
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1)).xyz;
    world_point=(MODEL_MATRIX*vec4(VERTEX,1)).xyz;
    authored_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 col=base_color.rgb;
    if(kind>.5 && kind<1.5) col=cavern_grass_color(world_point.xz);
    if(kind<.5){
        vec3 cell=floor(world_point*9.0)/9.0;
        float vein=sin(cell.x*.81+cell.y*1.6+sin(cell.z*.9))*.5+.5;
        col*=mix(vec3(.94,.98,1.0),vec3(1.04,1.02,.96),smoothstep(.25,.72,vein));
    }
    ALBEDO=col;
    ROUGHNESS=kind>.5 && kind<5.5 ? .96 : .72;
    if(kind>1.5 && kind<4.5) NORMAL=normalize((VIEW_MATRIX*vec4(authored_normal,0)).xyz);
}
void light(){
    float n=max(dot(NORMAL,LIGHT),0.0);
    float band=.20+.20*smoothstep(.10,.16,n)+.24*smoothstep(.36,.42,n)+.22*smoothstep(.61,.68,n)+.14*smoothstep(.83,.90,n);
    vec3 hue=mix(vec3(.64,.81,.90),vec3(1.01,1.0,.96),smoothstep(.20,.78,n));
    if(kind>.5 && kind<1.5){band=cavern_plant_diffuse(n);hue=cavern_plant_light_hue(n);}
    if(kind>1.5 && kind<4.5)hue=mix(vec3(.64,.84,.86),vec3(1.0,1.04,.91),smoothstep(.20,.76,n));
    DIFFUSE_LIGHT+=LIGHT_COLOR*band*hue*ATTENUATION/3.14159265;
}
