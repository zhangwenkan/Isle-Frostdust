extends "res://tools/capture_coastal_water.gd"

func save_view(label: String) -> void:
	await settle(12)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://artifacts/depth-composition-review/" + phase + "-" + label + ".png") == OK)
	print("DEPTH_CAPTURE ", label)

func parallax_report() -> Dictionary:
	position(-6.8)
	var points := {"foreground_cliff":Vector3(-9.4,3.0,6.8),"main_bamboo":Vector3(-7.4,4.0,-3.5),"back_grove":Vector3(-6.0,3.0,-35.0),"far_mountain":Vector3(-12.0,12.0,-142.0)}
	var before := {}
	for key in points:
		before[key] = island.camera.unproject_position(points[key]).x
	island.camera.position.x += 2.0
	var result := {}
	for key in points:
		result[key] = absf(island.camera.unproject_position(points[key]).x - before[key])
	position(-6.8)
	return result

func record_traversal() -> void:
	var folder := "res://artifacts/depth-composition-review/motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	var parallax := parallax_report()
	assert(parallax.foreground_cliff > parallax.main_bamboo)
	assert(parallax.main_bamboo > parallax.back_grove)
	assert(parallax.back_grove > parallax.far_mountain)
	position(-17.0)
	Input.action_press("move_right")
	var started := Time.get_ticks_msec()
	for frame in 420:
		set_time(frame/30.0)
		island._process(1.0/30.0)
		island.hero.pause()
		island.hero.frame = int(frame / 4.0) % island.hero.sprite_frames.get_frame_count(island.hero.animation)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder + "/%04d.jpg" % frame,0.94) == OK)
		if frame % 100 == 0:
			print("DEPTH_MOVIE_FRAME ",frame," hero_x=",island.hero_x)
	Input.action_release("move_right")
	assert(island.hero_x > 23.0)
	var output := FileAccess.open("res://artifacts/depth-composition-review/motion-verification.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"frames":420,"fps":30,"duration_seconds":14,"landed_x":island.hero_x,"camera_offset":str(island.camera_offset),"fov":island.gameplay_fov,"horizontal_pixels_for_2m_camera_move":parallax,"capture_seconds":(Time.get_ticks_msec()-started)/1000.0},"  "))
	print("DEPTH_MOVIE_COMPLETE ",JSON.stringify(parallax))

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hero.frame = 0
	island.hud.visible = false
	control_time(island)
	await settle(35)
	if "--movie" in OS.get_cmdline_user_args():
		await record_traversal()
		quit(0)
		return
	for point in [{"label":"midshot","x":-6.8},{"label":"west","x":-15.0},{"label":"bridge","x":7.8},{"label":"east","x":20.0}]:
		position(point.x)
		await save_view(point.label)
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	await save_view("no-dof")
	island.camera_effects.dof_blur_near_enabled = true
	island.camera_effects.dof_blur_far_enabled = true
	island.atmosphere.apply(10.5, 0.9)
	await save_view("overcast")
	quit(0)
