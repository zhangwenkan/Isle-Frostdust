shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
uniform sampler2D depth_texture:hint_depth_texture,filter_nearest;
uniform vec2 shoreline[32];
uniform mat4 author_world_to_local=mat4(1.0);
uniform bool swash_enabled=false;
uniform float scene_opacity=1.0;
uniform bool forest_land_mask_enabled=false;
uniform sampler2D forest_land_mask:filter_linear,repeat_disable;
uniform vec4 forest_land_bounds=vec4(0.0,0.0,1.0,1.0);
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
float wave(vec2 p){return sin(p.x*2.1+p.y*.64+TIME*.82)*.38+sin(p.y*3.3-p.x*.83-TIME*.67)*.25+sin(p.x*5.4+p.y*1.9-TIME*1.1)*.1;}
void fragment(){
    float d=texture(depth_texture,SCREEN_UV).r;
    vec4 behind=INV_PROJECTION_MATRIX*vec4(SCREEN_UV*2.-1.,d,1.);
    behind.xyz/=behind.w;
    float thickness=max(0.,-behind.z+VERTEX.z);
    float coast_distance=1000.;
    vec2 local_shore=(author_world_to_local*vec4(wp,1.)).xz;
    for(int i=0;i<31;i++){
        vec2 a=shoreline[i], b=shoreline[i+1], ab=b-a;
        float t=clamp(dot(local_shore-a,ab)/max(dot(ab,ab),.00001),0.,1.);
        coast_distance=min(coast_distance,length(local_shore-(a+ab*t)));
    }
    float shore=1.-smoothstep(.05,1.8,coast_distance);
    float farwater=smoothstep(20.,130.,-wp.z);
    float w=wave(wp.xz*.65);
    vec3 deep=vec3(.075,.175,.205);
    vec3 clear=vec3(.28,.43,.385);
    vec3 col=mix(deep,clear,shore*.75);
    col+=vec3(.012,.019,.022)*w;
    float streak=pow(max(0.,sin(wp.x*.9+wp.z*2.8+TIME*.6)),19.)*pow(max(0.,wave(wp.xz*.39)),3.);
    col+=vec3(.15,.18,.18)*streak;
    float crest=.25+.19*sin(TIME*.72+wp.x*.27)+.045*sin(wp.x*5.);
    float edge=(1.-smoothstep(.03,.14,abs(coast_distance-crest)))*smoothstep(-.7,.4,wave(wp.xz*.47));
    if(swash_enabled)edge=0.0;
    col=mix(col,vec3(.67,.72,.66),edge*.63);
    col=mix(col,vec3(.37,.45,.47),farwater*.82);
    // Far paintings contain their own pale cloudsea; the physical sea fades
    // into that middle layer instead of painting over the mountains and sky.
    float fade=1.-smoothstep(10.,36.,-wp.z+sin(wp.x*.15)*2.1);
    float transmission=swash_enabled?shore*exp(-thickness*.95):0.0;
    // The inland valley falls below the ocean plane. Its authored footprint
    // stays dry; otherwise this transparent sea paints over the rear groves.
    float inland=0.0;
    if(forest_land_mask_enabled){
        vec2 land_uv=(local_shore-forest_land_bounds.xy)/forest_land_bounds.zw;
        float in_bounds=step(0.0,land_uv.x)*step(0.0,land_uv.y)*step(land_uv.x,1.0)*step(land_uv.y,1.0);
        inland=texture(forest_land_mask,land_uv).r*in_bounds*smoothstep(24.0,29.0,-local_shore.y);
    }
    ALBEDO=col;ALPHA=fade*mix(1.0,.20,transmission)*(1.0-inland)*scene_opacity;
}
