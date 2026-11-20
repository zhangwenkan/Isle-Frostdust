shader_type spatial;
render_mode diffuse_lambert, specular_disabled, cull_disabled;

uniform vec4 base_color : source_color = vec4(.5,.6,.4,1.0);
uniform float surface_kind = 0.0;
uniform float wind_amount = 0.0;
uniform vec3 shade_tint : source_color = vec3(.55,.71,.76);
varying vec3 world_point;
varying vec3 world_shading_normal;

float hash21(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
void vertex() {
    vec3 wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    float anchor=surface_kind>2.5 ? clamp((wp.y-3.13)/.28,0.0,1.0) : clamp((wp.y-3.4)/4.5,0.0,1.0);
    VERTEX.x+=wind_amount*anchor*(sin(TIME*1.5+wp.x*.6+wp.z*.4)*.7+sin(TIME*.7+wp.z)*.3);
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
    world_shading_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment() {
    vec3 col=base_color.rgb;
    // Broad vegetation color fields; no per-pixel noise or random speckles.
    if(surface_kind>0.5 && surface_kind<1.5) {
        vec2 cell=floor(world_point.xz*12.0)/12.0;
        float patch=sin(cell.x*.65+sin(cell.y*.8))*cos(cell.y*.7-cell.x*.17);
        col*=mix(vec3(.90,1.0,1.02),vec3(1.03,1.02,.94),smoothstep(-.3,.5,patch));
    }
    ALBEDO=col;ROUGHNESS=surface_kind>1.5 ? .94 : .75;
    if(surface_kind>1.5) NORMAL=normalize((VIEW_MATRIX*vec4(world_shading_normal,0.0)).xyz);
}
void light() {
    float n=max(dot(NORMAL,LIGHT),0.0);
    // Controlled planes and cool half-tones. Godot applies ALBEDO afterwards;
    // multiplying it here again caused the earlier muddy color compression.
    float bands=.22+.23*smoothstep(.17,.23,n)+.30*smoothstep(.43,.49,n)+.25*smoothstep(.74,.80,n);
    vec3 hue=mix(shade_tint,vec3(1.0,.99,.93),smoothstep(.25,.7,n));
    if(surface_kind>0.5) hue=mix(vec3(.65,.86,.93),vec3(1.12,1.06,.83),smoothstep(.20,.78,n));
    float cloud=sin(world_point.x*.12+world_point.z*.18+TIME*.025)+.45*sin(world_point.z*.31-world_point.x*.14-TIME*.013);
    float cloud_shade=mix(.84,1.0,smoothstep(-.45,.7,cloud));
    DIFFUSE_LIGHT+=LIGHT_COLOR*hue*bands*ATTENUATION*cloud_shade/3.14159265;
}
