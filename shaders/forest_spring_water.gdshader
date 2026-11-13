shader_type spatial;
render_mode blend_mix,depth_draw_always,cull_disabled;
uniform sampler2D screen_color : hint_screen_texture,filter_linear_mipmap;
uniform int component=0;
varying vec3 world_position;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float field(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void vertex(){
 world_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
 if(component==1){VERTEX.x+=.012*sin(TIME*4.3+VERTEX.y*8.0);}
}
void fragment(){
 float ring=length((world_position.xz-vec2(37.158,-1.984))*vec2(1.,1.05));
 float ripple=sin(ring*17.-TIME*3.0)*exp(-ring*.85);
 float flow=sin(world_position.x*5.+world_position.z*8.+TIME*.7)*.45+sin(world_position.x*9.-world_position.z*3.-TIME*.43)*.25;
 NORMAL_MAP=normalize(vec3(.07*flow,.04*ripple,1.0))*.5+.5;
 NORMAL_MAP_DEPTH=.27;ROUGHNESS=.24;SPECULAR=.38;
 vec3 refraction=textureLod(screen_color,SCREEN_UV+vec2(flow,ripple)*.0008,0.).rgb;
 if(component==0){
  vec3 water=mix(vec3(.045,.155,.140),vec3(.12,.29,.23),smoothstep(-4.3,-.6,world_position.z));
  ALBEDO=mix(refraction,water,.41);
  float breakup=field(world_position.xz*3.+TIME*.21);
  float rings=smoothstep(.88,.99,sin(ring*12.-TIME*2.1+breakup*.35))*exp(-ring*1.25)*smoothstep(.2,.55,breakup);
  float landing=(1.-smoothstep(.12,.44+breakup*.13,ring))*(.75+.25*sin(TIME*3.));
  ALBEDO+=vec3(.20,.25,.18)*rings*.24+vec3(.36,.40,.32)*landing;
  ALPHA=.69;
 }else{
  float streak=field(vec2(UV.x*18.+sin(UV.y*5.-TIME*2.)*.2,UV.y*5.+TIME*3.));
  float pulse=field(vec2(UV.x*8.,UV.y*19.+TIME*8.));
  float edges=1.-smoothstep(.35,.49,abs(UV.x-.5));
  ALBEDO=mix(vec3(.10,.26,.24),vec3(.57,.65,.55),smoothstep(.48,.75,streak)*.64+smoothstep(.60,.9,pulse)*.25);
  ALPHA=(component==1?.35+.30*streak:.64)*edges+.07;
  ROUGHNESS=.32;
 }
}
