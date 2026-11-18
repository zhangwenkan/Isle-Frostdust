extends SceneTree
const OUT="res://artifacts/hero-forest-light-review/"
func _initialize():call_deferred("run")
func capture(name:String)->void:
	for tick in 10:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+name+".png")==OK)
func run()->void:
	var args=OS.get_cmdline_user_args();var prefix="pass1" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for path in ["hero_forest_light.gdshader","layered_forest_surface.gdshader","forest_role_leaf.gdshader","forest_depth_paint.gdshader","forest_depth_solid.gdshader","forest_layer_mist.gdshader","forest_local_air.gdshader","forest_sunray_veil.gdshader","layered_left.gdshader","layered_sea.gdshader","beach_sand.gdshader","beach_swash.gdshader","layered_distance.gdshader","layered_cloudsea.gdshader"]:
		var shader=load("res://shaders/"+path) as Shader;shader.code=shader.code.replace("TIME","8.0")
	var mat:ShaderMaterial=island.hero_lighting.material
	for shared in island.forest_light_materials:shared.set_shader_parameter("wind_time_override",8.0)
	var shots=[];var failures=[]
	if mat not in island.forest_light_materials:failures.append("Hero missing from shared light field")
	if island.forest_light_materials.size()!=316:failures.append("Unexpected shared binding count")
	for shot in [["forest_west_shade","forest_west_end",.65,"shade"],["forest_west_light","forest_west_mid",.8,"middle"],["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_entry","forest_west_gate",.6,"gate"],["beach","stair_bottom",.0,"beach"],["bridge_left","bridge_right",.5,"bridge"],["cave_mouth","cave_end",.7,"cave"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.,true);island._update_occluders(2.0);island.hero.pause();island.hero.frame=0
		if island.last_ground.is_empty():failures.append("Missing support "+shot[3])
		for time in ([0.0,5.0,10.0,15.0] if shot[3] in ["middle","clearing"] else [5.0]):
			for shared in island.forest_light_materials:shared.set_shader_parameter("forest_light_time_override",time)
			island.hero.material_override=null
			await capture(prefix+"-"+shot[3]+"-t%02d-before"%time)
			island.hero.material_override=mat
			await capture(prefix+"-"+shot[3]+"-t%02d-lit"%time)
			shots.append({"name":shot[3],"time":time,"position":str(island.hero.global_position),"author_position":str(island.get_node("World").to_local(island.hero.global_position)),"foot_screen":island.camera.unproject_position(island.hero.global_position),"head_screen":island.camera.unproject_position(island.hero.global_position+Vector3(0,2.1,0)),"source":island.hero_lighting.current_source})
		print("HERO_FOREST_CAPTURE ",shot[3])
	island.set_route_sample("forest_west_light","forest_west_mid",.8);island._update_occluders(2.0)
	for time in [0.0,5.0,10.0,15.0]:
		for shared in island.forest_light_materials:shared.set_shader_parameter("forest_light_time_override",time)
		mat.set_shader_parameter("review_mode",2)
		await capture(prefix+"-field-t%02d"%time)
	mat.set_shader_parameter("review_mode",0)
	var file=FileAccess.open(OUT+prefix+"-shots.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"shots":shots,"bindings":island.forest_light_materials.size(),"normal_atlases":island.hero_lighting.normal_atlases.keys(),"failures":failures},"  "))
	print("HERO_FOREST_STATIC_DONE");quit(0 if failures.is_empty() else 1)
