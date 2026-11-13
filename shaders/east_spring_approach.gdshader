shader_type spatial;
render_mode cull_disabled;
uniform sampler2D old_turf : source_color,filter_linear_mipmap,repeat_enable;
uniform sampler2D spring_paint : source_color,filter_nearest,repeat_disable;
varying vec3 world_pos;
void vertex(){world_pos=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
	vec3 old=texture(old_turf,vec2(UV.x*.5+.35,UV.y*.75+.125)).rgb;
	vec2 p=vec2(.13+UV.x*.30,.10+UV.y*.21);
	vec3 grove=texture(spring_paint,p).rgb;
	float lane=1.0-smoothstep(.14,.27,abs(UV.y-.5));
	grove=mix(grove,vec3(.46,.39,.24),lane*.65);
	float w=smoothstep(24.7,29.0,world_pos.x);
	ALBEDO=mix(old*.9,grove,w);
	ROUGHNESS=1.0;SPECULAR=0.0;
}
