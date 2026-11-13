shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
uniform sampler2D source_paint : source_color, filter_nearest, repeat_disable;
uniform int component = 0;
varying vec3 world_pos;
void vertex(){
	world_pos=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;
	if(component>=12 || component==4){
		float gust=sin(TIME*.83+world_pos.x*.7)+.32*sin(TIME*1.71+world_pos.z*.6);
		VERTEX.x+=gust*UV2.x*.028;
		VERTEX.z+=cos(TIME*.61+world_pos.x)*UV2.x*.011;
	}
}
void fragment(){
	vec2 p=vec2(UV.x*640.0-80.0,(1.0-UV.y)*400.0-20.0);
	vec2 sample_uv=UV;
	if(component==3){
		float inner=smoothstep(140.0,180.0,p.x)*(1.0-smoothstep(360.0,410.0,p.x));
		sample_uv.x+=floor(sin(p.y*.18+TIME*1.2)*1.25)*inner/640.0;
		sample_uv.y+=floor(sin(p.x*.09+TIME*.7)*1.05)*inner/400.0;
	}
	vec3 c=texture(source_paint,sample_uv).rgb;
	if(component==3){
		vec2 q=(p-vec2(338.0,211.0))/vec2(47.0,20.0);
		float dist=length(q);
		float pulse=sin(dist*16.0-TIME*4.0);
		float rings=smoothstep(.85,.98,pulse)*(1.0-smoothstep(.4,1.8,dist))*smoothstep(.20,.35,dist);
		c=mix(c,c*.77,rings*.30);
	}
	if(component==10){
		float white=smoothstep(.26,.58,max(c.r,max(c.g,c.b)));
		float streak=step(.5,fract(floor(p.x)*.371+floor(p.y+TIME*38.0)*.127));
		c=mix(c,c*mix(.68,1.03,streak),white*.60);
	}
	ALBEDO=c;
}
