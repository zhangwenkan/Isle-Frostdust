extends "res://tools/capture_coastal_water.gd"

func save_view(label: String) -> void:
	await settle(8)
	await RenderingServer.frame_post_draw
	var path := "res://artifacts/wuxia-style-review/" + phase + "-" + label + ".png"
	assert(root.get_texture().get_image().save_png(path) == OK)
	print("WUXIA_CAPTURE ", label)

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
	for point in [{"label":"midshot","x":-6.8},{"label":"bridge","x":7.8},{"label":"marker","x":1.1},{"label":"east","x":20.0}]:
		position(point.x)
		await save_view(point.label)
	island.atmosphere.apply(10.5, 0.9)
	position(-6.8)
	await save_view("overcast")
	island.atmosphere.apply(island.daylight_hour, island.cloud_cover)
	island.hud.visible = true
	await save_view("presentation")
	# Exercise the actual current movement code with live shader time restored.
	for material in controlled_materials:
		material.shader.code = material.shader.code.replace("review_time", "TIME").replace("uniform float TIME = 1.0;", "")
	position(2.6)
	island.set_process(true)
	Input.action_press("move_right")
	var start := Time.get_ticks_msec()
	var movement_frames := 0
	while island.hero_x < 16.0 and Time.get_ticks_msec() - start < 15000:
		await process_frame
		movement_frames += 1
	Input.action_release("move_right")
	island.set_process(false)
	assert(island.hero_x >= 16.0, "Crossing did not reach the east bank")
	print("WUXIA_MOVEMENT_OK frames=", movement_frames, " reached_x=", island.hero_x)
	quit(0)
