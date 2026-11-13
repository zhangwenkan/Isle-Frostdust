extends "res://tools/capture_forest_enclosure.gd"
func run_capture()->void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.hide()
	control_time(island)
	freeze_material(island.get_node("PixelBambooAtmosphere/BambooInteriorMist").material,"fog")
	set_time(1.0)
	var forest=island.get_node("PixelBambooAtmosphere")
	assert(forest.foreground_materials.size()==3)
	for x in [-14.0,-9.0,-1.0]:
		position(x);await picture("foreground-cross-%04.1f"%x)
		for mat in forest.foreground_materials:
			assert(mat.get_shader_parameter("actor_position").is_equal_approx(island.hero.global_position))
	position(-9.0)
	forest.set_process(false)
	for mat in forest.foreground_materials:mat.set_shader_parameter("actor_position",Vector3(900,900,900))
	await picture("foreground-without-character-clearance")
	forest.set_process(true)
	position(-15.2)
	var max_camera_step:=0.0
	for i in 360:
		var previous:Vector3=island.camera.position
		step_world(Vector2.RIGHT,1.0/60.0)
		max_camera_step=maxf(max_camera_step,island.camera.position.distance_to(previous))
		if i%12==0:await process_frame
	assert(island.hero_x>6.0)
	assert(max_camera_step<.35)
	for i in 120:
		step_world(Vector2.LEFT,1.0/60.0)
		if i%12==0:await process_frame
	var report={"foreground_material_count":3,"actor_uniforms_follow":true,"walk_return_frames":480,"max_camera_step_m_at_60hz":max_camera_step,"end_x":island.hero_x,"video_recorded":false}
	FileAccess.open(OUT+"visibility-verification.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("ENCLOSURE_VISIBILITY ",JSON.stringify(report))
	quit(0)
