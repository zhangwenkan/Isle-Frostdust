extends SceneTree
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var s=load("res://scenes/layered_island.tscn").instantiate();root.add_child(s);current_scene=s
	s.manual_control=false;s.camera_locked=true;s.hud.hide()
	for i in 8:await process_frame
	print("ACTOR_PROPS ",s.hero.get_property_list().filter(func(p):return p.name in ["alpha_cut","alpha_scissor_threshold","texture_filter","billboard"]))
	print("PROPS ",s.hero.alpha_cut," ",s.hero.alpha_scissor_threshold," ",s.hero.texture_filter," ",s.hero.transparency," ",s.hero.modulate)
	s.hero.no_depth_test=true
	await shot("diagnostic-no-depth")
	s.hero.alpha_cut=SpriteBase3D.ALPHA_CUT_DISABLED
	await shot("diagnostic-alpha")
	s.hero.no_depth_test=false
	await shot("diagnostic-alpha-depth")
	var tex=s.hero.sprite_frames.get_frame_texture(s.hero.animation,0)
	tex.get_image().save_png("res://artifacts/layered-island-build/actor-loaded-texture.png")
	var mat=ShaderMaterial.new();var shader=Shader.new()
	shader.code="shader_type spatial; render_mode unshaded,cull_disabled; uniform sampler2D painting:source_color,filter_linear; void fragment(){vec4 c=texture(painting,UV);ALBEDO=c.rgb;ALPHA=c.a;ALPHA_SCISSOR_THRESHOLD=.3;}"
	mat.shader=shader;mat.set_shader_parameter("painting",tex)
	s.hero.billboard=BaseMaterial3D.BILLBOARD_DISABLED;s.hero.material_override=mat
	await shot("diagnostic-custom")
	quit()
func shot(n):
	for i in 4:await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://artifacts/layered-island-build/"+n+".png")
