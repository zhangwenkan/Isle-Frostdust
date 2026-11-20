shader_type spatial;
render_mode unshaded,cull_disabled;
uniform vec4 base_color:source_color=vec4(.42,.56,.57,1);
varying vec3 wp;
varying vec3 wn;
void vertex(){wp=(MODEL_MATRIX*vec4(VERTEX,1)).xyz;wn=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    float shade=.78+.17*smoothstep(-.3,.8,dot(wn,normalize(vec3(-.6,.8,.5))));
    vec3 col=base_color.rgb*shade;
    float mist=1.0-smoothstep(-2.0,14.0,wp.y);
    col=mix(col,vec3(.48,.60,.60),mist*.60);
    ALBEDO=col;ROUGHNESS=.98;
}
