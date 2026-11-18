extends SceneTree
const OUT="res://artifacts/forest-wind-mist-review/"
func _initialize():call_deferred("run")
func run():
	var args=OS.get_cmdline_user_args();var prefix="motion" if args.is_empty() else str(args[0])+"-motion"
	DirAccess.make_dir_recursive_absolute(OUT+prefix+"-frames")
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.hero.pause()
	# Let the initial viewport render before reading it on the first sample.
	for warmup in 8:await process_frame
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	var locked:Transform3D=island.camera.transform
	var samples=[];var failures=[];var bound_materials=0
	for node in island.get_node("World").find_children("Forest_Bamboo_Role_*","MeshInstance3D",true,false):
		var expected:Dictionary=island.layout.forest_extension.layer_roles.wind_bindings.get(str(node.name),{})
		for s in node.mesh.get_surface_count():
			var mat=node.get_surface_override_material(s) as ShaderMaterial
			if not mat or expected.is_empty():failures.append("Unbound bamboo "+str(node.name));continue
			bound_materials+=1
			if not is_equal_approx(float(mat.get_shader_parameter("wind_strength")),float(expected.amplitude)):failures.append("Wind amplitude not applied "+str(node.name))
			if not (mat.get_shader_parameter("bamboo_root") as Vector3).is_equal_approx(island.v3(expected.root)):failures.append("Wind root mismatch "+str(node.name))
	for tick in 528:
		if tick==288:island._unhandled_key_input(event)
		var input=Vector2.ZERO
		if tick>=288 and tick<336:input=Vector2.RIGHT
		if tick>=384 and tick<480:input=Vector2.LEFT
		island.advance_input(input,1.0/24.0);await process_frame
		if tick<288 and not island.camera.transform.is_equal_approx(locked):failures.append("Idle locked camera moved")
		if island.last_ground.is_empty() and failures.is_empty():failures.append("Missing support")
		if tick%2==0:
			var im=root.get_texture().get_image();im.resize(960,540,Image.INTERPOLATE_LANCZOS)
			assert(im.save_jpg(OUT+prefix+"-frames/frame-%04d.jpg"%(tick/2),.94)==OK)
		if tick%24==0:
			samples.append({"frame":tick,"input":str(input),"anchor":island.current_anchor,"camera":str(island.camera.position),"sea_opacity":island.sea_material.get_shader_parameter("scene_opacity")})
			print("FOREST_MOTION_PROGRESS ",tick,"/528")
	var file=FileAccess.open(OUT+prefix+"-check.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine_fps":24,"capture_fps":12,"duration_seconds":22,"fixed_camera_idle_seconds":12,"bound_materials":bound_materials,"move_speed":island.MOVE_SPEED,"failures":failures,"samples":samples},"  "))
	print("FOREST_WIND_MOTION_DONE");quit(0 if failures.is_empty() else 1)
