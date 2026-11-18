extends SceneTree
const OUT="res://artifacts/hero-forest-light-review/"
func _initialize():call_deferred("run")
func run()->void:
	DirAccess.make_dir_recursive_absolute(OUT+"motion-frames")
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island);current_scene=island
	island.manual_control=false;island.hud.hide();island.set_process(false)
	island.reset_actor("forest_west_mid")
	for warmup in 8:await process_frame
	var event=InputEventKey.new();event.physical_keycode=KEY_F5;event.pressed=true;island._unhandled_key_input(event)
	var locked:Transform3D=island.camera.transform
	var mat:ShaderMaterial=island.hero_lighting.material
	var ray:Vector3=(island.get_node("World").global_basis.inverse()*(-island.get_node("CoastalSun").global_basis.z)).normalized()
	var failures=[];var samples=[];var facing_seen={};var atlases_seen={}
	for shared in island.forest_light_materials:
		if not (shared.get_shader_parameter("forest_ray_direction") as Vector3).is_equal_approx(ray):failures.append("Different solar projection "+shared.shader.resource_path)
	if island.forest_light_materials.size()!=316:failures.append("Missing shared material")
	for tick in 576:
		if tick==192:island._unhandled_key_input(event)
		var input=Vector2.ZERO
		if tick>=192 and tick<240:input=Vector2.RIGHT
		if tick>=288 and tick<384:input=Vector2.LEFT
		if tick>=432 and tick<528:input=Vector2.RIGHT
		island.advance_input(input,1.0/24.0)
		island._update_camera(1.0/24.0);island._update_occluders(1.0/24.0)
		await process_frame
		if tick<192 and not island.camera.transform.is_equal_approx(locked):failures.append("Fixed camera moved")
		if island.last_ground.is_empty() and failures.is_empty():failures.append("Missing support")
		if mat.get_shader_parameter("mirror_sign")!=(-1.0 if island.hero.flip_h else 1.0):failures.append("Mirrored normal mismatch")
		facing_seen["left" if island.hero.flip_h else "right"]=true
		atlases_seen[island.hero_lighting.current_source]=true
		if tick%2==0:
			RenderingServer.force_draw(false)
			var image=root.get_texture().get_image();image.resize(960,540,Image.INTERPOLATE_LANCZOS)
			assert(image.save_jpg(OUT+"motion-frames/frame-%04d.jpg"%(tick/2),.94)==OK)
		if tick%48==0:
			print("HERO_FOREST_MOTION ",tick,"/576")
			samples.append({"frame":tick,"anchor":island.current_anchor,"animation":str(island.hero.animation),"source":island.hero_lighting.current_source,"mirror":island.hero.flip_h,"position":str(island.hero.global_position),"camera":str(island.camera.position)})
	var file=FileAccess.open(OUT+"motion-check.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine_fps":24,"capture_fps":12,"duration_seconds":24,"fixed_camera_seconds":8,"bindings":island.forest_light_materials.size(),"ray":str(ray),"facing_seen":facing_seen.keys(),"atlases_seen":atlases_seen.keys(),"move_speed":island.MOVE_SPEED,"failures":failures,"samples":samples},"  "))
	print("HERO_FOREST_MOTION_DONE");quit(0 if failures.is_empty() else 1)
