shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never,fog_disabled;
uniform float phase=0.0;
uniform float density=.26;
uniform float opacity=1.0;
float h(vec2 p){return fract(sin(dot(p,vec2(91.7,317.3)))*43758.54);}
float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1)),f.x),f.y);}
void fragment(){
    vec2 p=UV*vec2(10,4)+phase;
    p+=vec2(n(p*.61+TIME*.016),n(p*.73-TIME*.011))*.9;
    float shape=n(p+TIME*.007)*.65+n(p*2.1-TIME*.014)*.35;
    float veil=sin(clamp(UV.y,0.,1.)*3.14159);
    ALBEDO=mix(vec3(.34,.46,.50),vec3(.72,.73,.67),UV.y);
    ALPHA=smoothstep(.28,.76,shape)*pow(veil,1.7)*density*opacity;
}
