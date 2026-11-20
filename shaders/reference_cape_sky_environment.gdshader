shader_type sky;
uniform float cape_amount=0.0;
uniform vec3 sun_direction=vec3(-.63,.06,-.78);
float hash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
void sky(){
    vec3 d=normalize(EYEDIR);
    float h=smoothstep(-.12,.48,d.y);
    vec3 color=mix(vec3(.68,.64,.56),vec3(.77,.63,.51),h);
    float glow=pow(max(0.0,dot(d,normalize(sun_direction))),6.0);
    color+=vec3(.19,.07,.003)*glow;
    float cloud=noise(vec3(d.xz*3.1,d.y*4.0+TIME*.012));
    cloud=.7*cloud+.3*noise(vec3(d.xz*7.0+3.0,d.y*8.0-TIME*.018));
    color=mix(color,vec3(.81,.72,.62),smoothstep(.50,.67,cloud)*h*.32);
    float broad=noise(vec3(d.xz*4.8+vec2(TIME*.006,-TIME*.008),d.y*6.0+sin(TIME*.017)*.2));
    float ribbon=smoothstep(.43,.69,broad)*(1.0-smoothstep(.13,.47,d.y));
    color=mix(color,vec3(.79,.71,.65),ribbon*.28);
    float disc=1.0-smoothstep(.014,.027,length(d-normalize(sun_direction)));
    color=mix(color,vec3(1.0,.83,.48),disc);
    COLOR=mix(pow(vec3(.63,.69,.70),vec3(2.2)),pow(color,vec3(2.2)),cape_amount);
}
