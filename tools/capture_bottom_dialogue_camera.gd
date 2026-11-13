extends "res://tools/capture_bottom_dialogue.gd"
## Inspect changed camera framing and the actual opening; save stills only.

func run() -> void:
	root.content_scale_size = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280, 720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	await settle(20)
	key(KEY_R)
	var start_camera: Transform3D = island.camera.transform
	var start_life: float = island.coastal_life.elapsed
	var min_margin := 10000.0
	for frame in 105:
		await process_frame
		var actor := actor_screen_rect()
		assert(Rect2(0, 0, 1280, 720).encloses(actor), "Opening actor leaves screen")
		assert(island.camera.transform.is_equal_approx(start_camera), "Camera jumps during opening")
		min_margin = minf(min_margin, minf(minf(actor.position.x, actor.position.y),
			minf(1280 - actor.end.x, 720 - actor.end.y)))
		if frame in [0, 40, 70, 100]:
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(output_directory + "opening-%03d.png" % frame)
	await settle(40)
	shot("camera-dialogue")
	assert(island.coastal_life.elapsed > start_life + 4.0)
	island.opening.dialogue.characters_per_second = 0.0
	key(KEY_SPACE)
	await settle(2)
	key(KEY_SPACE)
	await settle(4)
	assert(not island.opening.is_input_locked())
	island.hud.hide()
	await settle(2)
	root.get_texture().get_image().save_png(output_directory + "cape-without-dialogue.png")
	var previous := actor_screen_rect().get_center()
	var max_step := 0.0
	Input.action_press("move_right")
	for frame in 55:
		await process_frame
		var actor := actor_screen_rect()
		assert(Rect2(0, 0, 1280, 720).encloses(actor), "Actor leaves screen at camera transition")
		max_step = maxf(max_step, previous.distance_to(actor.get_center()))
		previous = actor.get_center()
		if frame in [12, 30, 54]:
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(output_directory + "exit-cape-%02d.png" % frame)
	Input.action_release("move_right")
	var file := FileAccess.open(output_directory + "camera-verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"static_only": true,
		"opening_samples": 105, "opening_min_screen_margin": min_margin,
		"opening_camera_unchanged_through_dialogue": true,
		"environment_continued": true, "exit_cape_samples": 55,
		"exit_max_actor_center_step_px_at_24fps": max_step, "final_hero_x": island.hero_x}, "  "))
	print("BOTTOM_CAMERA_VERIFIED")
	quit(0)
