shader_type spatial;
render_mode diffuse_burley, specular_disabled;
uniform bool is_turf=false;
uniform bool is_patch=false;
uniform float depth_haze=0.0;
uniform sampler2D turf_paint : source_color, filter_linear_mipmap_anisotropic;
varying vec3 world_position;
varying vec3 world_normal;
void vertex(){
    world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 pigment=COLOR.rgb;
    vec2 local=mod(world_position.xz+vec2(19.0,8.0),vec2(5.0,2.8));
    vec2 uv=vec2((local.x+8.0)/26.0,(local.y+1.0)/14.0);
    vec3 painted=texture(turf_paint,uv).rgb;
    if(is_turf){
        // Reuse an existing road-free ink grass area at matching world-space density.
        pigment=mix(pigment,painted,.62);
        ALBEDO=pigment*.70;
        EMISSION=pigment*.23;
    }else{
        float sky=max(dot(normalize(world_normal),normalize(vec3(-.65,.70,.45))),0.0);
        // Turf creeps across the lip of each exposure; quad boundaries are not
        // painted as straight rectangular color changes on the hillside.
        vec2 q=(UV-vec2(.48,.50))/vec2(.55,.60);
        float radius=length(q)+.10*sin(UV.y*8.0+UV.x*5.0);
        float rock=is_patch?1.0-smoothstep(.55,1.0,radius):1.0;
        vec3 grass=mix(vec3(.19,.25,.105),painted,.68);
        ALBEDO=mix(grass*.70,pigment*.82,rock);
        EMISSION=mix(grass*.23,pigment*(.065+.15*sky),rock);
    }
    float distance_haze=max(depth_haze,smoothstep(14.0,76.0,-world_position.z)*.36);
    float valley_shadow=smoothstep(7.0,13.0,-world_position.z)*(1.0-smoothstep(20.0,27.0,-world_position.z));
    ALBEDO=mix(ALBEDO,ALBEDO*vec3(.67,.81,.80),valley_shadow*.62);
    EMISSION*=1.0-valley_shadow*.18;
    ALBEDO=mix(ALBEDO,vec3(.19,.26,.24)*.75,distance_haze);
    EMISSION=mix(EMISSION,vec3(.19,.26,.24)*.65,distance_haze);
    ROUGHNESS=1.0;
}
