shader_type spatial;
render_mode cull_disabled, diffuse_lambert, specular_disabled;

uniform sampler2D color_atlas : source_color, filter_nearest, repeat_disable;
uniform sampler2D volume_atlas : filter_linear, repeat_disable;
uniform sampler2D surface_atlas : filter_linear, repeat_disable;
uniform bool has_surface = false;
uniform vec4 sprite_tint : source_color = vec4(1.0);
uniform bool has_volume = false;
uniform float mirror_sign = 1.0;
uniform float light_share = .78;
uniform float normal_strength = 1.25;
uniform float light_wrap = .95;
uniform float ground_lift = 0.0;
uniform float sprite_pixel_size = .0037;
uniform float leg_blend_height = .72;
uniform vec2 sprite_offset = vec2(0.0,340.0);
uniform vec2 frame_size = vec2(512.0,768.0);
uniform vec4 frame_uv_rect = vec4(0.0,0.0,1.0,1.0);
uniform float foot_curve[65];
varying vec2 card_xy;

float foot_offset(float x){
    float index=clamp((x+.70)/1.40*64.0,0.0,64.0);
    int a=min(int(index),63);
    return mix(foot_curve[a],foot_curve[a+1],index-float(a));
}

void vertex(){
    // Extend only the transparent margin of the existing quad for downhill toes.
    // No mesh is created; upper-body projection and the source atlas are unchanged.
    if(has_volume && VERTEX.y<0.0) VERTEX.y-=.34;
    card_xy=VERTEX.xy;
    // Translation is applied to the rendered card, not the gameplay/camera root.
    MODELVIEW_MATRIX = VIEW_MATRIX * MODEL_MATRIX;
    MODELVIEW_MATRIX[3] += VIEW_MATRIX * vec4(0.0,ground_lift,0.0,0.0);
}
void fragment(){
    vec2 atlas_uv=UV;
    bool inside_frame=true;
    if(has_volume){
        float y=card_xy.y;
        float offset=foot_offset(card_xy.x);
        // Inverse of a contact displacement fading to zero below the knee.
        // Source action height remains in the image; torso, head and arms do not warp.
        if(y<leg_blend_height){
            y=y>=offset ? (y-offset)/(1.0-offset/leg_blend_height) : y-offset;
        }
        vec2 pixel=vec2(card_xy.x/sprite_pixel_size-sprite_offset.x,
                       -y/sprite_pixel_size+sprite_offset.y)+frame_size*.5;
        if(mirror_sign<0.0) pixel.x=frame_size.x-pixel.x;
        vec2 frame_uv=pixel/frame_size;
        inside_frame=all(greaterThanEqual(frame_uv,vec2(0.0))) && all(lessThan(frame_uv,vec2(1.0)));
        atlas_uv=frame_uv_rect.xy+frame_uv*frame_uv_rect.zw;
    }
    vec4 paint=texture(color_atlas,atlas_uv)*sprite_tint;
    if(!inside_frame) paint.a=0.0;
    ALPHA=paint.a;
    ALPHA_SCISSOR_THRESHOLD=.5;
    vec3 n=vec3(0.0,0.0,1.0);
    if(has_volume){
        n=texture(volume_atlas,atlas_uv).rgb*2.0-1.0;
        n.xy*=normal_strength;
        n.x*=mirror_sign;
        n=normalize(n);
    }
    NORMAL=normalize(mat3(VIEW_MATRIX)*mat3(MODEL_MATRIX)*n);
    // Only the outermost ink receives a small pigment lift. Eye/cloth ink remains.
    // A warm neutral floor lets the actual light color reach the rim without a halo.
    float edge=has_surface ? texture(surface_atlas,atlas_uv).r : 0.0;
    float ink=1.0-smoothstep(.012,.060,max(paint.r,max(paint.g,paint.b)));
    vec3 pigment=paint.rgb+vec3(.012,.014,.013)*edge*ink;
    // Opening/action sheets have no matching surface maps and retain their palette mix.
    float share=has_volume ? light_share : .32;
    ALBEDO=pigment*share;
    EMISSION=pigment*(1.0-share);
    ROUGHNESS=1.0;
}

void light(){
    // Broad matte response, with real light direction and shadow attenuation.
    // Wrapped diffuse preserves the readability of painted front faces in backlight.
    float lambert=max(dot(NORMAL,LIGHT),0.0);
    float wrapped=max((dot(NORMAL,LIGHT)+light_wrap)/(1.0+light_wrap),0.0);
    float response=mix(lambert,wrapped,has_volume ? .80 : 0.0);
    // Godot multiplies accumulated diffuse irradiance by ALBEDO afterwards.
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*response/PI;
}
