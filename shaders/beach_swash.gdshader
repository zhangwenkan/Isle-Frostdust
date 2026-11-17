shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never,blend_mix;
#include "res://shaders/beach_swash_field.gdshaderinc"
uniform float pixel_density=48.0;
uniform float film_opacity=.23;
uniform float foam_amount=.90;
void fragment(){
    vec2 p=floor(UV2*pixel_density)/pixel_density;
    float front=swash_front(p.x),phase=swash_phase(p.x);
    float water=smoothstep(front-.025,front+.055,p.y);
    float time=shoreline_time();
    float rim=1.0-smoothstep(.085,.47,abs(p.y-front));
    vec2 flow=vec2(p.x*3.5+time*.16,p.y*5.6+time*.31);
    float body=swash_noise(flow)*.64+swash_noise(flow*2.07+13.8)*.36;
    float lace=1.0-smoothstep(.025,.12,abs(body-.51));
    float flecks=smoothstep(.34,.61,swash_noise(vec2(p.x*4.7,p.y*7.1-time*.24)));
    float trailing=smoothstep(.24,.48,phase)*(1.0-smoothstep(.76,.99,phase));
    trailing*=smoothstep(front,front+.12,p.y)*(1.0-smoothstep(front+.70,front+1.8,p.y));
    float foam=clamp((rim*mix(.07,1.0,flecks)+trailing*lace*.78)*foam_amount,0.,1.);
    float shimmer=pow(max(0.,sin(p.x*6.4+p.y*9.3+time*1.1+body*4.)),18.);
    vec3 water_color=vec3(.115,.225,.218)+vec3(.035,.042,.033)*shimmer;
    vec3 foam_color=vec3(.72,.75,.67);
    ALBEDO=mix(water_color,foam_color,foam);
    float ends=smoothstep(0.,.033,UV.x)*(1.-smoothstep(.967,1.,UV.x));
    float far_edge=smoothstep(0.,.13,UV.y);
    ALPHA=(water*film_opacity*(1.-foam)+foam*.92)*ends*far_edge;
}
