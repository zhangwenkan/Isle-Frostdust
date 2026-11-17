shader_type spatial;
render_mode cull_disabled, diffuse_burley;
uniform sampler2D painting : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
uniform vec4 grove_tint : source_color = vec4(1.0);
uniform float forest_air=0.0;
uniform bool use_texture=true;
uniform bool vertex_tint=false;
uniform bool sand=false;
uniform bool foliage=false;
uniform bool actor_clearance=false;
uniform vec3 actor_focus=vec3(0.0);
uniform vec3 viewer_position=vec3(0.0);
uniform float wind_strength=0.0;
uniform mat4 author_world_to_local=mat4(1.0);
varying vec3 authored_position;
varying vec3 world_position;
void vertex(){
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    authored_position=(author_world_to_local*vec4(wp,1.0)).xyz;
    float gust=sin(TIME*.62+wp.x*.43+wp.z*.23)*.60;
    gust+=sin(TIME*1.07+wp.x*.81)*.23;
    VERTEX.x+=gust*UV2.x*wind_strength;
    VERTEX.z+=sin(TIME*.71+wp.x*.40)*UV2.x*wind_strength*.27;
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
}
void fragment(){
    vec3 color=(use_texture?texture(painting,UV).rgb:vec3(1.0))*tint.rgb;
    if(vertex_tint)color*=COLOR.rgb;
    if(foliage)color*=vec3(1.12,1.13,1.04);
    if(actor_clearance){
        vec3 ray=actor_focus-viewer_position;
        float t=dot(world_position-viewer_position,ray)/dot(ray,ray);
        float radius=length(world_position-viewer_position-ray*t);
        float mask=(1.0-smoothstep(.43,.95,radius))*step(.015,t)*(1.0-smoothstep(.96,1.0,t));
        // Stable spatial stipple clears only leaves crossing the actor; the
        // rest of each grove stays opaque and keeps its depth and shadow.
        float grain=fract(sin(dot(floor(world_position.xz*95.0)+floor(world_position.y*87.0),vec2(12.9898,78.233)))*43758.5453);
        if(grain<mask*.96)discard;
    }
    if(sand){
        float wet=1.0-smoothstep(-.11,.095,authored_position.y+.008*sin(authored_position.x*2.4));
        color=mix(color,color*vec3(.66,.73,.79),wet*.72);
        ROUGHNESS=mix(.97,.66,wet);
    }else{ROUGHNESS=.97;}
    ALBEDO=color*grove_tint.rgb*(1.0-forest_air);SPECULAR=.06;
    // Opaque woodland retains correct depth while local air reduces distant
    // contrast. This supplements the actual volumes between the nearer rows.
    EMISSION=vec3(.12,.16,.11)*forest_air;
}
