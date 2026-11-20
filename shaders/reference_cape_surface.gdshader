shader_type spatial;
render_mode cull_disabled,diffuse_burley;
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_enable;
uniform sampler2D forest_ground:source_color,filter_linear_mipmap_anisotropic,repeat_disable;
uniform bool neck=false;
uniform bool grass=false;
uniform bool use_texture=true;
uniform vec4 tint:source_color=vec4(1.0);
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 author_position;
void vertex(){
    author_position=(author_world_to_local*MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    if(grass){
        float bend=sin(TIME*.85+author_position.x*.31+author_position.z*.23)*.035;
        VERTEX.x+=bend*UV2.x;VERTEX.z+=sin(TIME*.71+author_position.x*.26)*UV2.x*.022;
    }
}
void fragment(){
    vec3 col=use_texture?texture(painting,UV).rgb:tint.rgb;
    if(neck){
        vec2 uv=vec2((author_position.x+50.0)/54.0,(-author_position.z+4.0)/40.0);
        vec3 earth=texture(forest_ground,uv).rgb;
        float stone=1.0-smoothstep(-68.5,-61.2,author_position.x);
        col=mix(earth,col,stone);
    }
    ALBEDO=col*.93;ROUGHNESS=.91;SPECULAR=.13;
}
