extends SceneTree

const OUT := "res://artifacts/rest-rise-color-review/"
var island: Node3D
var phase := "before"
var samples: Array = []


func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--phase="):
			phase = arg.trim_prefix("--phase=")
	call_deferred("run")


func run() -> void:
	root.content_scale_size = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280, 720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	# Hide the entire layer once; start_dialogue only toggles its child Screen.
	island.opening.dialogue.hide()
	# Warm the renderer, then restart the actual animation and signal path.
	for i in 30:
		await process_frame
	var reset := InputEventKey.new()
	reset.keycode = KEY_R
	reset.pressed = true
	island._unhandled_key_input(reset)
	if phase == "before":
		island.hero.sprite_frames = load("res://assets/characters/rest_rise_right/rest_rise_chin.tres")
		island.hero.play(&"rest_rise_right")
	DirAccess.make_dir_recursive_absolute(OUT + phase + "-frames")
	var origin: Vector3 = island.hero.position
	for frame in 145:
		await process_frame
		await RenderingServer.frame_post_draw
		assert(island.hero.position == origin)
		if frame >= 80:
			assert(root.get_texture().get_image().save_png(OUT + phase + "-frames/%03d.png" % frame) == OK)
		if frame >= 94 and frame <= 110:
			samples.append({"capture_frame":frame,"animation":island.hero.animation,"sprite_frame":island.hero.frame,
				"modulate":str(island.hero.modulate),"pixel_size":island.hero.pixel_size,"offset":str(island.hero.offset),
				"shaded":island.hero.shaded,"phase":island.opening.phase})
	var file := FileAccess.open(OUT + phase + "-runtime.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(samples, "  "))
	print("COLOR_CAPTURE_COMPLETE ", phase)
	quit(0)
