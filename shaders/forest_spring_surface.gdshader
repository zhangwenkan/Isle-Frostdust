shader_type spatial;
render_mode cull_disabled;
uniform sampler2D component_paint : source_color, filter_nearest_mipmap, repeat_disable;
uniform int component = 0;
uniform vec3 tint : source_color = vec3(1.0);
varying vec3 world_position;
void vertex(){
 world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
 if(component>=3){
  float gust=.58+.42*sin(TIME*.31+world_position.x*.17+world_position.z*.13);
  float breeze=sin(TIME*.82+world_position.x*.61+world_position.z*.29)*gust;
  VERTEX.x+=breeze*UV2.x*(component==3?.045:.025);
  VERTEX.z+=cos(TIME*.63+world_position.x*.25)*UV2.x*.019;
 }
}
void fragment(){
 vec4 paint=texture(component_paint,UV);
 ALBEDO=paint.rgb*tint;
 if(component>=3){ALPHA=paint.a;ALPHA_SCISSOR_THRESHOLD=.48;}
 ROUGHNESS=.92;SPECULAR=.12;
 float woods=smoothstep(25.0,29.0,world_position.x);
 float back=1.-smoothstep(-10.0,-1.5,world_position.z);
 float shade=mix(1.0,mix(.90,.73,back),woods);
 if(component==0){
  ALBEDO*=shade;
  float near_old=1.0-smoothstep(24.0,26.8,world_position.x);
  ALBEDO=mix(ALBEDO,ALBEDO*vec3(1.04,1.09,1.05),near_old);
 }
 if(component==1){ALBEDO*=.89;AO=.83;AO_LIGHT_AFFECT=.15;}
 if(component==2){ALBEDO*=.87;AO=.8;AO_LIGHT_AFFECT=.15;}
 if(component==3){ALBEDO*=mix(.78,.64,back);BACKLIGHT=vec3(.05,.065,.025);}
 if(component==4){ALBEDO*=shade*.90;BACKLIGHT=vec3(.035,.055,.02);}
}
