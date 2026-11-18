shader_type spatial;
render_mode cull_disabled, diffuse_lambert, specular_disabled;
#include "res://shaders/forest_role_light.gdshaderinc"

uniform sampler2D color_atlas:source_color,filter_linear_mipmap,repeat_disable;
uniform sampler2D volume_atlas:filter_linear_mipmap,repeat_disable;
uniform vec4 sprite_tint:source_color=vec4(1.0);
uniform mat4 author_world_to_local=mat4(1.0);
uniform bool has_volume=false;
uniform float mirror_sign=1.0;
uniform float hero_light_enabled=1.0;
uniform float normal_strength=.85;
uniform float light_share=.86;
uniform float light_wrap=.65;
// Review only: 1 = original paint, 2 = the shared canopy field.
uniform int review_mode=0;
varying vec3 authored_position;
varying mat3 card_to_view;

void vertex(){
    // Match Godot's fixed-Y sprite, including its camera-facing shadow pass.
    mat4 card=mat4(
        vec4(normalize(cross(vec3(0.0,1.0,0.0),MAIN_CAM_INV_VIEW_MATRIX[2].xyz)),0.0),
        vec4(0.0,1.0,0.0,0.0),
        vec4(normalize(cross(MAIN_CAM_INV_VIEW_MATRIX[0].xyz,vec3(0.0,1.0,0.0))),0.0),
        MODEL_MATRIX[3]);
    MODELVIEW_MATRIX=VIEW_MATRIX*card;
    MODELVIEW_NORMAL_MATRIX=mat3(MODELVIEW_MATRIX);
    card_to_view=mat3(MODELVIEW_MATRIX);
    // Interpolated across the unchanged sprite: head, sleeves and feet occupy
    // different points along the same solar projection used by the ground.
    authored_position=(author_world_to_local*card*vec4(VERTEX,1.0)).xyz;
}

void fragment(){
    // AnimatedSprite3D supplies atlas UVs and mirrors them with flip_h.
    vec4 paint=texture(color_atlas,UV)*sprite_tint;
    ALPHA=paint.a;
    ALPHA_SCISSOR_THRESHOLD=.30;
    float participation=role_extent(authored_position)*hero_light_enabled;
    vec3 n=vec3(0.0,0.0,1.0);
    if(has_volume){
        vec3 mapped=texture(volume_atlas,UV).rgb*2.0-1.0;
        mapped.xy*=normal_strength;
        mapped.x*=mirror_sign;
        n=normalize(mix(n,normalize(mapped),participation));
    }
    NORMAL=normalize(card_to_view*n);
    float share=mix(1.0,light_share,participation);
    ALBEDO=paint.rgb*share;
    // Keep the painted eye/cloth lines readable in moving shade.
    EMISSION=paint.rgb*(1.0-share);
    ROUGHNESS=1.0;
    if(review_mode>0){
        ALBEDO=vec3(0.0);
        EMISSION=review_mode==1?paint.rgb:vec3(forest_aperture(authored_position,TIME));
    }
}

void light(){
    float participation=role_extent(authored_position)*hero_light_enabled;
    float facing=dot(NORMAL,LIGHT);
    float lambert=max(facing,0.0);
    float wrapped=max((facing+light_wrap)/(1.0+light_wrap),0.0);
    float response=mix(lambert,wrapped,participation*.80);
    float canopy=mix(1.0,role_sun(authored_position,TIME),hero_light_enabled);
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*response*canopy/PI;
}
