shader_type spatial;
render_mode cull_disabled,diffuse_burley;
uniform sampler2D painting:source_color,filter_linear_mipmap_anisotropic,repeat_enable;
void fragment(){ALBEDO=mix(texture(painting,UV).rgb,vec3(.49,.53,.52),.73);ROUGHNESS=1.0;SPECULAR=0.0;}
