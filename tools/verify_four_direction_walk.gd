extends SceneTree
## Exercise the real island input, animation resources and road/bridge limits.

var island: Node3D
var captures := false
var checks: Array[String] = []
const OUTPUT := "res://artifacts/green-walk-integration/"

func _initialize() -> void:
	captures = "--capture-walk" in OS.get_cmdline_user_args()
	call_deferred("run_checks")

func check(condition: bool, label: String) -> void:
	if not condition:
		push_error("WALK_CHECK_FAILED: " + label)
		quit(1)
		assert(condition, label)
	checks.append(label)

func reset_actor(x := -6.8) -> void:
	island.hero_x = x
	island.hero_path_offset = 0.0
	island._position_hero()

func input_step(action: String, delta := 0.1) -> void:
	Input.action_press(action)
	island._process(delta)
	Input.action_release(action)

func screenshot(label: String, action: String) -> void:
	reset_actor()
	input_step(action, 0.05)
	island._update_camera(0.0, true)
	island.hero.frame = island.hero.sprite_frames.get_frame_count(island.hero.animation) / 2
	island.hero.pause()
	for i in 12:
		await process_frame
	await RenderingServer.frame_post_draw
	var path := OUTPUT + label + ".png"
	check(root.get_texture().get_image().save_png(path) == OK, "screenshot " + label)

func run_checks() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hud.visible = false
	var frames: SpriteFrames = island.hero.sprite_frames
	check(island.hero.animation == &"idle_right" and not island.hero.is_playing(), "startup uses new right standing reference")
	check(is_equal_approx(island.hero.pixel_size, 0.0037) and island.hero.offset == Vector2(0, 340), "native scale and anchor apply before first input")
	check(frames.get_frame_count("walk_right") == 26, "right retains all 26 new frames")
	check(frames.get_frame_count("walk_up") == 29, "up retains all 29 new frames")
	check(frames.get_frame_count("walk_down") == 24, "down retains all 24 new frames")
	var atlas_images: Dictionary = {}
	for animation in ["walk_right", "walk_up", "walk_down"]:
		check(frames.get_animation_speed(animation) == 24.0, animation + " at 24 fps")
		check(frames.get_animation_loop(animation), animation + " loops")
		check(frames.get_frame_texture(animation, 0).get_size() == Vector2(512, 768), animation + " native resolution")
		for index in frames.get_frame_count(animation):
			var texture := frames.get_frame_texture(animation, index) as AtlasTexture
			check(texture.atlas.resource_path.begins_with("res://assets/characters/green_three_walk/"), animation + " uses new atlas " + str(index))
			if not atlas_images.has(texture.atlas):
				atlas_images[texture.atlas] = texture.atlas.get_image()
			var frame_image: Image = atlas_images[texture.atlas].get_region(Rect2i(texture.region))
			check(frame_image.get_used_rect().end.y == 724, animation + " foot anchor " + str(index))
		var idle: String = animation.replace("walk_", "idle_")
		check(frames.get_frame_count(idle) == 1 and not frames.get_animation_loop(idle), idle + " uses one standing frame")
		check(frames.get_frame_texture(idle, 0).get_image().get_used_rect().end.y == 724, idle + " shares foot anchor")
		island._set_hero_animation(animation, true)
		island.hero.set_frame_and_progress(0, 0.0)
		await create_timer(0.15).timeout
		check(island.hero.frame > 0, animation + " advances in the actual scene")

	reset_actor()
	var start: Vector3 = island.hero.position
	input_step("move_up")
	check(island.hero.position.z < start.z and is_equal_approx(island.hero_x, start.x), "W moves away from camera")
	check(island.hero.animation == &"walk_up" and not island.hero.flip_h and island.hero.is_playing(), "W plays unmirrored back walk")
	var screen_height_up: float = 768 * island.hero.pixel_size
	check(is_equal_approx(screen_height_up, 384 * 0.0074), "native up frames retain world scale")
	island._process(0.1)
	check(island.hero.animation == &"idle_up" and not island.hero.is_playing(), "release W stands facing back")
	input_step("move_down")
	check(island.hero.position.is_equal_approx(start), "S returns along depth axis")
	check(island.hero.animation == &"walk_down" and not island.hero.flip_h, "S plays unmirrored front walk")
	island._process(0.1)
	check(island.hero.animation == &"idle_down" and not island.hero.is_playing(), "release S stands facing front")
	input_step("move_left")
	check(island.hero.animation == &"walk_right" and island.hero.flip_h, "A keeps mirrored right walk")
	check(is_equal_approx(island.hero.pixel_size, 0.0037) and island.hero.offset == Vector2(0, 340), "sideways turn keeps identical scale and anchor")
	island._process(0.1)
	check(island.hero.animation == &"idle_right" and island.hero.flip_h and not island.hero.is_playing(), "release A stands with new mirrored reference")
	input_step("move_up")
	check(not island.hero.flip_h, "vertical turn clears left mirror")
	input_step("move_right")
	check(island.hero.animation == &"walk_right" and not island.hero.flip_h, "D keeps right walk")
	check(island.hero.position.is_equal_approx(Vector3(start.x, island.hero.position.y, start.z - island.HERO_SPEED * 0.1)), "horizontal movement remains reversible")

	reset_actor()
	Input.action_press("move_right")
	Input.action_press("move_up")
	island._process(0.1)
	Input.action_release("move_right")
	Input.action_release("move_up")
	var diagonal := Vector2(island.hero_x + 6.8, island.hero_path_offset)
	check(is_equal_approx(diagonal.length(), island.HERO_SPEED * 0.1), "diagonal input has no speed boost")
	check(island.hero.animation == &"walk_right", "diagonal tie consistently selects horizontal")
	for key in [KEY_UP, KEY_DOWN]:
		reset_actor()
		var arrow := InputEventKey.new()
		arrow.keycode = key
		arrow.pressed = true
		Input.parse_input_event(arrow)
		Input.flush_buffered_events()
		island._process(0.1)
		check(island.hero.animation == (&"walk_up" if key == KEY_UP else &"walk_down"), "arrow key " + str(key) + " selects vertical walk")
		var release := arrow.duplicate() as InputEventKey
		release.pressed = false
		Input.parse_input_event(release)
		Input.flush_buffered_events()
	for x in [-17.0, -6.8, 5.5, 10.0, 20.0]:
		reset_actor(x)
		input_step("move_up", 3.0)
		check(is_equal_approx(island.hero_path_offset, -0.55), "rear boundary at x=" + str(x))
		input_step("move_up")
		check(not island.hero.is_playing(), "blocked rear movement stops animation")
		input_step("move_down", 3.0)
		check(is_equal_approx(island.hero_path_offset, 0.55), "front boundary at x=" + str(x))
	reset_actor(3.2)
	for i in 120:
		input_step("move_right", 0.05)
	check(island.hero_x > 14.5, "existing route still crosses bridge to east landing")
	for side in [-1.0, 1.0]:
		reset_actor(3.2)
		island.hero_path_offset = side * 0.55
		island._position_hero()
		for i in 95:
			input_step("move_right", 0.05)
			if island.hero_x > 4.2 and island.hero_x < 14.5:
				check(island.hero.position.z >= -0.3001 and island.hero.position.z <= 0.8001, "bridge rail clearance at " + str(island.hero_x) + " side " + str(side))
	input_step("move_right", 100.0)
	check(is_equal_approx(island.hero_x, 23.7), "east endpoint retained")
	input_step("move_left", 100.0)
	check(is_equal_approx(island.hero_x, -18.0), "west endpoint retained")
	var event := InputEventKey.new()
	event.keycode = KEY_R
	event.pressed = true
	island._unhandled_key_input(event)
	check(is_equal_approx(island.hero_x, -6.8) and is_zero_approx(island.hero_path_offset), "R resets both axes")
	check(island.hero.animation == &"idle_right" and not island.hero.flip_h and island.hero.frame == 0, "R resets facing and standing frame")

	if captures:
		await screenshot("up", "move_up")
		await screenshot("down", "move_down")
		await screenshot("left", "move_left")
		await screenshot("right", "move_right")
	var file := FileAccess.open(OUTPUT + "verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed": true, "checks": checks, "screenshots": captures}, "  "))
	print("FOUR_DIRECTION_WALK_PASS: ", checks.size(), " checks; screenshots=", captures)
	quit(0)
