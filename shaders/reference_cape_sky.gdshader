shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never;
uniform float opacity=0.0;
float hash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
void fragment(){
    float h=1.0-UV.y;
    vec3 low=vec3(.57,.60,.59),high=vec3(.72,.60,.50);
    vec3 col=mix(low,high,smoothstep(.25,.90,h));
    float glow=exp(-pow((UV.x-.31)*3.4,2.0))*smoothstep(.30,.8,h);
    col+=vec3(.18,.075,.008)*glow;
    float clouds=noise(vec3(UV*vec2(6.0,9.0),TIME*.012));
    clouds=.70*clouds+.30*noise(vec3(UV*vec2(13.0,17.0)+8.0,TIME*.019));
    float cloud=smoothstep(.47,.66,clouds)*smoothstep(.42,.95,h);
    col=mix(col,vec3(.75,.70,.62),cloud*.28);
    ALBEDO=col;ALPHA=opacity;
}
