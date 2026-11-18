extends SceneTree
const OUT="res://artifacts/forest-light-depth-review/"
func _initialize():call_deferred("run")
func run():
	DirAccess.make_dir_recursive_absolute(OUT+"motion-frames")
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.hero.pause()
	for warmup in 8:await process_frame
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	var locked:Transform3D=island.camera.transform
	var ray:Vector3=(island.get_node("World").global_basis.inverse()*(-island.get_node("CoastalSun").global_basis.z)).normalized()
	var failures=[];var samples=[];var shader_counts={}
	for mat in island.forest_light_materials:
		if not (mat.get_shader_parameter("forest_ray_direction") as Vector3).is_equal_approx(ray):failures.append("Different solar projection "+mat.shader.resource_path)
		if not is_equal_approx(float(mat.get_shader_parameter("forest_light_strength")),1.0):failures.append("Disabled light field "+mat.shader.resource_path)
		shader_counts[mat.shader.resource_path]=int(shader_counts.get(mat.shader.resource_path,0))+1
	for path in ["layered_forest_surface.gdshader","forest_role_leaf.gdshader","forest_depth_paint.gdshader","forest_depth_solid.gdshader","forest_layer_mist.gdshader","forest_local_air.gdshader","forest_sunray_veil.gdshader"]:
		if not shader_counts.has("res://shaders/"+path):failures.append("Missing shared-light role "+path)
	if int(shader_counts.get("res://shaders/forest_local_air.gdshader",0))!=3:failures.append("Not all three fog volumes bound")
	for tick in 672:
		if tick==432:island._unhandled_key_input(event)
		var input=Vector2.ZERO
		if tick>=432 and tick<480:input=Vector2.RIGHT
		if tick>=528 and tick<624:input=Vector2.LEFT
		island.advance_input(input,1.0/24.0);await process_frame
		if tick<432 and not island.camera.transform.is_equal_approx(locked):failures.append("Fixed camera moved")
		if island.last_ground.is_empty() and failures.is_empty():failures.append("Missing support")
		if tick%2==0:
			var im=root.get_texture().get_image();im.resize(960,540,Image.INTERPOLATE_LANCZOS)
			assert(im.save_jpg(OUT+"motion-frames/frame-%04d.jpg"%(tick/2),.94)==OK)
		if tick%48==0:
			print("FOREST_LIGHT_MOTION ",tick,"/672")
			samples.append({"frame":tick,"anchor":island.current_anchor,"camera":str(island.camera.position),"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity")})
	var file=FileAccess.open(OUT+"motion-check.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine_fps":24,"capture_fps":12,"duration_seconds":28,"fixed_camera_seconds":18,"ray":str(ray),"shader_binding_counts":shader_counts,"move_speed":island.MOVE_SPEED,"failures":failures,"samples":samples},"  "))
	print("FOREST_LIGHT_MOTION_DONE");quit(0 if failures.is_empty() else 1)
