shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never,blend_add;
void fragment(){float a=1.0-smoothstep(.12,.50,length(UV-.5));ALBEDO=vec3(1.0,.48,.08);EMISSION=ALBEDO*2.0;ALPHA=a*.85;}
