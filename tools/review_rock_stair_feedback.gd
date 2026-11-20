extends SceneTree
const OUT="res://artifacts/rock-forest-style-review/feedback-steps/"
func _initialize():call_deferred("run")
func run():
	Engine.time_scale=0.0;root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720);root.content_scale_mode=Window.CONTENT_SCALE_MODE_VIEWPORT;root.content_scale_aspect=Window.CONTENT_SCALE_ASPECT_KEEP
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for mat in island.forest_light_materials:mat.set_shader_parameter("forest_light_time_override",0.0)
	island.set_route_sample("cape_stair_top","cape_stair_bottom",.48);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island.hero.pause();island.hero.frame=0;island._update_occluders(0.0)
	var mats=[]
	for obj in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		for index in obj.mesh.get_surface_count():
			var mat=obj.get_surface_override_material(index) as ShaderMaterial
			if mat and mat.shader.resource_path=="res://shaders/rock_forest_wash.gdshader":mats.append(mat)
	for variant in ["current","bias-check","no-normal","plain-no-normal","plain-no-shadow"]:
		island.get_node("CoastalSun").shadow_bias=.08 if variant=="bias-check" else .018
		island.get_node("CoastalSun").shadow_normal_bias=.65 if variant=="bias-check" else .23
		if variant=="plain-no-shadow":
			for light in island.find_children("*","Light3D",true,false):light.shadow_enabled=false
		for mat in mats:
			mat.set_shader_parameter("normal_strength",.72 if variant in ["current","bias-check"] else 0.0)
			if variant=="plain-no-normal":
				var shader=Shader.new();shader.code=mat.shader.code.replace("ALBEDO=texture(painting,UV).rgb;","ALBEDO=vec3(.20,.21,.18);");mat.shader=shader
		for frame in 25:await process_frame
		RenderingServer.force_draw(false);assert(root.get_texture().get_image().save_png(OUT+variant+".png")==OK)
	print("STATIC_FEEDBACK_DIAGNOSIS_COMPLETE; only temporary materials in this process changed");quit()
