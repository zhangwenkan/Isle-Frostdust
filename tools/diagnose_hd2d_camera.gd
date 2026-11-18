extends SceneTree
const OUT="res://artifacts/hd2d-camera-diagnosis/"
func _initialize():call_deferred("run")
func capture(name:String)->void:
	for frame in 8:await process_frame
	RenderingServer.force_draw(false)
	assert(root.get_texture().get_image().save_png(OUT+name+".png")==OK)
func run()->void:
	DirAccess.make_dir_recursive_absolute(OUT)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.set_process(false);island.manual_control=false;island.hud.hide();island.hero.pause()
	for path in ["hero_forest_light.gdshader","layered_forest_surface.gdshader","forest_role_leaf.gdshader","forest_depth_paint.gdshader","forest_depth_solid.gdshader","forest_layer_mist.gdshader","forest_local_air.gdshader","forest_sunray_veil.gdshader","layered_left.gdshader","layered_sea.gdshader"]:
		var shader=load("res://shaders/"+path) as Shader;shader.code=shader.code.replace("TIME","8.0")
	for mat in island.forest_light_materials:
		mat.set_shader_parameter("wind_time_override",8.0)
		mat.set_shader_parameter("forest_light_time_override",10.0)
	var original_offset:Vector3=island.v3(island.layout.camera.physical_offset)
	var distance=original_offset.length()
	var report=[]
	for location in [["forest_west_light","forest_west_mid",.8,"middle"],["forest_west_gate","forest_west_light",.8,"clearing"]]:
		island.set_route_sample(location[0],location[1],location[2]);island.hero.pause()
		var focus:Vector3=island.camera_focus_world
		var baseline:Vector3=island.camera.position
		var height=(island.camera.unproject_position(island.hero.position+Vector3(0,2.1,0))-island.camera.unproject_position(island.hero.position)).length()
		for setting in [["current",0.0,15.24,distance,22.5],["zoom_only",0.0,15.24,distance,17.8],["ground_depth",0.0,23.5,distance,22.5],["closer_angle",7.0,23.5,27.0,22.5],["closer_same_angle",0.0,15.24,24.0,22.5],["closer_low_side",8.0,10.0,25.0,22.5]]:
			var yaw=deg_to_rad(float(setting[1]));var pitch=deg_to_rad(float(setting[2]));var radius=float(setting[3])
			island.camera.position=focus+Vector3(sin(yaw)*cos(pitch),sin(pitch),cos(yaw)*cos(pitch))*radius
			island.camera.look_at(focus);island.camera.fov=float(setting[4])
			if setting[0] in ["ground_depth","closer_angle","closer_same_angle","closer_low_side"]:
				# Hold the original character's projected height while changing depth.
				var actual=(island.camera.unproject_position(island.hero.position+Vector3(0,2.1,0))-island.camera.unproject_position(island.hero.position)).length()
				island.camera.fov=rad_to_deg(2.0*atan(tan(deg_to_rad(island.camera.fov)*.5)*actual/height))
			island._update_occluders(2.0)
			await capture(location[3]+"-"+setting[0])
			var author_offset:Vector3=island.get_node("World").global_basis.inverse()*(island.camera.position-focus)
			var depth_samples=[]
			for z in [-6.0,-12.8,-20.0,-29.0,-43.0,-64.0]:
				var p=Vector3(-31.4,6.18,z)
				var world_point:Vector3=island.get_node("World").to_global(p)
				var depth=-island.camera.to_local(world_point).z
				var one_meter=(island.camera.unproject_position(world_point+Vector3.RIGHT*.5)-island.camera.unproject_position(world_point-Vector3.RIGHT*.5)).length()
				depth_samples.append({"author_z":z,"view_depth":depth,"screen_px_per_world_m":one_meter})
			var foot=island.camera.unproject_position(island.hero.position)
			var head=island.camera.unproject_position(island.hero.position+Vector3(0,2.1,0))
			report.append({"location":location[3],"variant":setting[0],"camera":str(island.camera.position),"fov_vertical":island.camera.fov,"fov_horizontal":rad_to_deg(2.0*atan(tan(deg_to_rad(island.camera.fov)*.5)*16.0/9.0)),"author_offset":str(author_offset),"author_pitch":rad_to_deg(atan2(author_offset.y,Vector2(author_offset.x,author_offset.z).length())),"world_pitch":setting[2],"character_2_1m_height_px":(head-foot).length(),"foot_screen":str(foot),"layer_depths":depth_samples})
	var file=FileAccess.open(OUT+"camera-measurements.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
	print("HD2D_CAMERA_DIAGNOSIS_DONE");quit()
