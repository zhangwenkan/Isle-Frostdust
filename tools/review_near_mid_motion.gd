extends SceneTree
const OUT="res://artifacts/near-mid-depth-review/"
func _initialize():call_deferred("run")
func run()->void:
	var args=OS.get_cmdline_user_args()
	var prefix="" if args.is_empty() else str(args[0])+"-"
	var frame_dir=OUT+prefix+"motion-frames/"
	DirAccess.make_dir_recursive_absolute(frame_dir)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false);island.reset_actor("forest_west_mid")
	for warmup in 8:await process_frame
	var key=InputEventKey.new();key.physical_keycode=KEY_F5;key.pressed=true;island._unhandled_key_input(key)
	var locked=island.camera.transform;var locked_fov=island.camera.fov
	var failures=[];var samples=[];var seen={};var height_min=INF;var height_max=0.0
	var near:Vector3=island.v3(island.layout.forest_extension.layer_roles.wind_bindings.Forest_Bamboo_Role_Front_01.root)
	var near_world:Vector3=island.get_node("World").to_global(near)
	var far_world:Vector3=island.get_node("World").to_global(Vector3(near.x,near.y,-43.0))
	var last_near=island.camera.unproject_position(near_world);var last_far=island.camera.unproject_position(far_world)
	var movement_ratios=[]
	for tick in 672:
		if tick==96:island._unhandled_key_input(key)
		var input=Vector2.ZERO
		if tick>=96 and tick<144:input=Vector2.LEFT
		if tick>=192 and tick<312:input=Vector2.RIGHT
		if tick>=360 and tick<456:input=Vector2.LEFT
		if tick>=504 and tick<624:input=Vector2.RIGHT
		island.advance_input(input,1.0/24.0);island._update_camera(1.0/24.0);island._update_occluders(1.0/24.0)
		await process_frame
		if tick<96 and (not island.camera.transform.is_equal_approx(locked) or not is_equal_approx(locked_fov,island.camera.fov)):failures.append("Fixed framing moved")
		if island.last_ground.is_empty():failures.append("Missing imported support")
		elif absf(island.hero.position.y-float(island.last_ground.height)-.014)>.003:failures.append("Feet separated from imported support")
		if island.hero.material_override!=island.hero_lighting.material:failures.append("Lost character shared light")
		if island.hero_lighting.material.get_shader_parameter("mirror_sign")!=(-1.0 if island.hero.flip_h else 1.0):failures.append("Wrong mirrored normal")
		seen[island.current_anchor]=true
		var height=(island.camera.unproject_position(island.hero.position+Vector3(0,2.1,0))-island.camera.unproject_position(island.hero.position)).length()
		height_min=minf(height_min,height);height_max=maxf(height_max,height)
		var current_near=island.camera.unproject_position(near_world);var current_far=island.camera.unproject_position(far_world)
		if current_far.distance_to(last_far)>.05 and absf(island.camera.fov-30.9616)<.03:
			movement_ratios.append(current_near.distance_to(last_near)/current_far.distance_to(last_far))
		last_near=current_near;last_far=current_far
		if tick%2==0:
			RenderingServer.force_draw(false)
			var im=root.get_texture().get_image();im.resize(960,540,Image.INTERPOLATE_LANCZOS)
			assert(im.save_jpg(frame_dir+"frame-%04d.jpg"%(tick/2),.94)==OK)
		if tick%48==0:
			print("NEAR_MID_MOTION ",tick,"/672")
			samples.append({"tick":tick,"anchor":island.current_anchor,"fov":island.camera.fov,"hero_height_px":height,"camera":str(island.camera.position),"actor":str(island.hero.position),"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity")})
	var file=FileAccess.open(OUT+prefix+"motion-check.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine_fps":24,"capture_fps":12,"duration_seconds":28,"fixed_camera_seconds":4,"move_speed":island.MOVE_SPEED,"bindings":island.forest_light_materials.size(),"anchors_seen":seen.keys(),"hero_height_min_px":height_min,"hero_height_max_px":height_max,"near_far_movement_ratios":movement_ratios,"samples":samples,"failures":failures},"  "))
	print("NEAR_MID_MOTION_DONE");quit(0 if failures.is_empty() else 1)
