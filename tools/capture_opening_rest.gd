extends SceneTree
## Exercise the real opening, animation signal, input dispatch and player unlock.

const OUT := "res://artifacts/opening-rest-dialogue-review/"
var island: Node3D
var samples: Array = []
var animation_ends := 0
var completed_dialogues := 0


func _initialize() -> void:
	call_deferred("run")


func key(code: Key) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = pressed
		Input.parse_input_event(event)


func click_continue() -> void:
	var button: BaseButton = island.opening.dialogue.advance_button
	var point := button.get_global_rect().get_center()
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = point
		event.pressed = pressed
		Input.parse_input_event(event)


func shot(label: String) -> void:
	assert(root.get_texture().get_image().save_png(OUT + label + ".png") == OK)
	print("OPENING_SHOT ", label)


func run() -> void:
	root.content_scale_size = Vector2i(1280, 720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280, 720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.hero.animation_finished.connect(func(): animation_ends += 1)
	island.opening.dialogue.dialogue_finished.connect(func(_id): completed_dialogues += 1)
	# Let initial GPU pipelines settle, then replay through the user's R action.
	for i in 30:
		await process_frame
	key(KEY_R)
	var start_position: Vector3 = island.hero.position
	var start_camera: Transform3D = island.camera.transform
	var start_life: float = island.coastal_life.elapsed
	animation_ends = 0
	var first_dialogue_frame := -1
	DirAccess.make_dir_recursive_absolute(OUT + "frames")
	Input.action_press("move_right")
	for frame in 360:
		if frame == 170:
			assert(island.opening.dialogue._page == 0)
			key(KEY_SPACE)
		if frame == 235:
			assert(island.opening.dialogue._page == 1)
			Input.action_release("move_right")
			click_continue()
		if frame == 252:
			assert(not island.opening.is_input_locked())
			assert(island.hud.visible)
			Input.action_press("move_right")
		if frame == 320:
			Input.action_release("move_right")
		await process_frame
		await RenderingServer.frame_post_draw
		if frame < 234:
			assert(island.hero.position.is_equal_approx(start_position))
			assert(island.camera.transform.is_equal_approx(start_camera))
			assert(island.opening.is_input_locked())
			assert(not island.hud.visible)
		if island.opening.phase == island.opening.Phase.DIALOGUE and first_dialogue_frame < 0:
			first_dialogue_frame = frame
			assert(animation_ends == 1)
			assert(island.hero.animation == &"idle_right")
			assert(island.hero.offset == island.HERO_SPRITE_OFFSET)
		if frame in [0, 24, 50, 70, 98, 104, 150, 210, 245, 300, 359]:
			shot("frame-%03d" % frame)
		if frame % 24 == 0:
			samples.append({"time":frame / 24.0,"phase":island.opening.phase,"animation":island.hero.animation,"frame":island.hero.frame,"hero_x":island.hero_x,"life_time":island.coastal_life.elapsed})
		assert(root.get_texture().get_image().save_jpg(OUT + "frames/%04d.jpg" % frame, .94) == OK)
	assert(first_dialogue_frame >= 100 and first_dialogue_frame <= 104)
	assert(completed_dialogues == 1)
	assert(island.hero_x > island.HERO_START_X + 8.0)
	assert(island.coastal_life.elapsed > start_life + 14.0)
	# Replay also cancels an in-progress opening and an active dialogue safely.
	key(KEY_R)
	await process_frame
	assert(island.hero_x == island.HERO_START_X)
	assert(island.hero.animation == &"rest_rise_right")
	key(KEY_R)
	await process_frame
	assert(island.hero.frame <= 1)
	assert(not island.opening.dialogue.is_dialogue_active())
	for i in 110:
		await process_frame
	assert(island.opening.dialogue.is_dialogue_active())
	key(KEY_R)
	await process_frame
	assert(island.opening.phase == island.opening.Phase.RISING)
	assert(not island.opening.dialogue.is_dialogue_active())
	assert(completed_dialogues == 1)
	var report := {"frames":360,"fps":24,"seconds":15,"first_dialogue_frame":first_dialogue_frame,"animation_end_signal":true,"keyboard_page_and_mouse_close":true,"movement_locked_during_opening":true,"movement_restored_after_dialogue":true,"environment_continued":true,"replay_during_rise_and_dialogue":true,"samples":samples}
	var file := FileAccess.open(OUT + "verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	print("OPENING_VERIFIED ", JSON.stringify(report))
	quit(0)
