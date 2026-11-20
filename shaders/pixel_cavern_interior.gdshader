shader_type spatial;
render_mode unshaded,cull_disabled;
varying vec3 wp;
varying vec3 wn;
uniform bool stone_steps=false;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1)).xyz;wn=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    float depth=clamp((-wp.z-3.0)/6.0,0.0,1.0);
    vec3 col=mix(vec3(.035,.075,.087),vec3(.009,.018,.028),depth);
    if(stone_steps)col*=.75+.45*max(wn.y,0.0);
    ALBEDO=col;
    ROUGHNESS=.74;
}
