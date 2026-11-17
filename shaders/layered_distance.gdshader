shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, fog_disabled;
uniform sampler2D painting : source_color, filter_linear_mipmap, repeat_disable;
uniform float opacity=1.0;
uniform bool sky=false;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1)),f.x),f.y);}
float field(vec2 p){float n=noise(p)*.57;n+=noise(p*2.07+4.3)*.28;n+=noise(p*4.1+2.7)*.15;return n;}
void fragment(){
    vec4 c=texture(painting,UV);
    if(sky){
        vec2 p=UV*vec2(7.0,4.0);
        p+=vec2(field(p*.4+TIME*.013),field(p*.5-TIME*.009))*.75;
        float density=field(p+vec2(TIME*.008,TIME*.004));
        float cloud=smoothstep(.44,.70,density)*smoothstep(.05,.25,UV.y)*.32;
        c.rgb=mix(c.rgb,vec3(.84,.80,.74),cloud);
    }
    ALBEDO=c.rgb;ALPHA=c.a*opacity;
}
