shader_type spatial;
render_mode unshaded, cull_disabled;
varying vec3 wp;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}
void fragment(){
    vec2 p=floor(wp.xz*7.0)/7.0;
    float wave=sin(p.x*.6+p.y*1.6+TIME*.65)+sin(p.x*.13-p.y*.6+TIME*.3);
    vec3 col=mix(vec3(.045,.16,.19),vec3(.075,.25,.28),smoothstep(-25.0,10.0,p.y));
    float ripple=step(1.48,wave)*step(.1,sin(p.x*1.7-p.y*.2));
    col=mix(col,vec3(.18,.37,.38),ripple*.18);
    ALBEDO=col;
}
