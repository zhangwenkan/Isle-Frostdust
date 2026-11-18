extends SceneTree
const OUT="res://artifacts/near-mid-depth-review/"
func _initialize():call_deferred("run")
func capture(path:String)->void:
	for frame in 8:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+path+".png")==OK)
func run()->void:
	var args=OS.get_cmdline_user_args();var prefix="before" if args.is_empty() else str(args[0])
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.hero.pause()
	for path in ["hero_forest_light.gdshader","layered_forest_surface.gdshader","forest_role_leaf.gdshader","forest_depth_paint.gdshader","forest_depth_solid.gdshader","forest_layer_mist.gdshader","forest_local_air.gdshader","forest_sunray_veil.gdshader","layered_left.gdshader","layered_sea.gdshader","beach_sand.gdshader","beach_swash.gdshader","layered_distance.gdshader","layered_cloudsea.gdshader"]:
		var shader=load("res://shaders/"+path) as Shader;shader.code=shader.code.replace("TIME","8.0")
	for mat in island.forest_light_materials:mat.set_shader_parameter("wind_time_override",8.0);mat.set_shader_parameter("forest_light_time_override",10.0)
	var report=[]
	for shot in [["forest_west_shade","forest_west_end",1.0,"end"],["forest_west_mid","forest_west_shade",.6,"shade"],["forest_west_light","forest_west_mid",.8,"middle"],["forest_west_gate","forest_west_light",.8,"clearing"],["forest_west_entry","forest_west_gate",.6,"gate"],["forest_end","forest_west_entry",.45,"connection"],["beach","stair_bottom",.0,"beach"],["bridge_left","bridge_right",.5,"bridge"]]:
		island.set_route_sample(shot[0],shot[1],shot[2]);island.facing="right";island.facing_left=false;island._update_actor(false,0.0,true);island._update_occluders(2.0);island.hero.pause();island.hero.frame=0
		await capture(prefix+"-"+shot[3])
		var foot=island.camera.unproject_position(island.hero.position);var head=island.camera.unproject_position(island.hero.position+Vector3(0,2.1,0))
		report.append({"name":shot[3],"camera":str(island.camera.position),"actor":str(island.hero.position),"fov":island.camera.fov,"hero_height_px":(foot-head).length(),"supported":not island.last_ground.is_empty(),"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity")})
		if shot[3]=="middle":
			var field_mat=island.hero_lighting.material;field_mat.set_shader_parameter("review_mode",2)
			await capture(prefix+"-middle-field");field_mat.set_shader_parameter("review_mode",0)
			var fov=island.camera.fov;island.camera.fov=fov*.55
			var near=island.camera.attributes.dof_blur_near_enabled;var far=island.camera.attributes.dof_blur_far_enabled
			island.camera.attributes.dof_blur_near_enabled=false;island.camera.attributes.dof_blur_far_enabled=false
			await capture(prefix+"-middle-close")
			island.camera.fov=fov;island.camera.attributes.dof_blur_near_enabled=near;island.camera.attributes.dof_blur_far_enabled=far
	var file=FileAccess.open(OUT+prefix+"-static-check.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
	print("NEAR_MID_STATIC_DONE ",prefix);quit()
