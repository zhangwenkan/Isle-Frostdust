extends SceneTree
## Real rendered lifecycle at fixed 24 fps, including replay and --skip-opening.
const OUT := "res://artifacts/overhead-opening-review/"
var island: Node3D
var samples: Array = []
var animation_ends := 0
var dialogue_ends := 0

func _initialize() -> void:
	call_deferred("run")

func key(code: Key) -> void:
	for pressed in [true,false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = pressed
		Input.parse_input_event(event)

func require(condition: bool, message: String) -> void:
	if not condition:
		push_error(message)
		quit(1)
		assert(condition,message)

func wait_frames(count: int) -> void:
	for i in count: await process_frame

func check_title_center() -> void:
	var rect: Rect2 = island.opening.title_group.get_global_rect()
	require(rect.get_center().distance_to(root.get_visible_rect().get_center()) < 2.0,"Title must stay centered")

func run() -> void:
	root.content_scale_size = Vector2i(1280,720)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.size = Vector2i(1280,720)
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	if "--skip-opening" in OS.get_cmdline_user_args():
		await wait_frames(20)
		require(not island.opening.is_input_locked(),"Skipped opening locked input")
		require(not island.opening.title_layer.visible,"Skipped opening shows title")
		require(island.hero.animation != &"rest_rise_right","Skipped opening plays rise")
		var start_x: float = island.hero_x
		Input.action_press("move_right")
		await wait_frames(12)
		Input.action_release("move_right")
		require(island.hero_x > start_x + .5,"Skip must allow walking")
		key(KEY_R)
		await process_frame
		require(not island.opening.title_layer.visible,"Skip replay must stay skipped")
		FileAccess.open(OUT+"skip-verification.json",FileAccess.WRITE).store_string('{"skip_input_title_walk_replay":true}')
		quit(0)
		return
	# This checks the initial camera before any rendered frame, not just replay.
	require(island.camera.global_basis.z.dot(Vector3.UP) > .999999,"First camera must be exactly overhead")
	require(island.hero.frame == 0 and not island.hero.is_playing(),"Intro must hold the original lying frame")
	await wait_frames(30)
	key(KEY_R)
	await process_frame
	var start_position: Vector3 = island.hero.position
	var start_life: float = island.coastal_life.elapsed
	island.hero.animation_finished.connect(func(): animation_ends += 1)
	island.opening.dialogue.dialogue_finished.connect(func(_id): dialogue_ends += 1)
	var first_rise := -1
	var first_dialogue := -1
	var last_camera: Transform3D = island.camera.transform
	var last_phase: int = island.opening.phase
	var boundary_distance := 0.0
	var boundary_angle := 0.0
	Input.action_press("move_right")
	DirAccess.make_dir_recursive_absolute(OUT+"frames")
	for frame in 444:
		await process_frame
		await RenderingServer.frame_post_draw
		var opening: Node = island.opening
		require(island.hero.position.is_equal_approx(start_position),"Movement leaked into cinematic")
		require(opening.is_input_locked() and not island.hud.visible,"Cinematic input or HUD state")
		if opening.phase == opening.Phase.ESTABLISHING:
			require(island.hero.frame == 0 and not island.hero.is_playing(),"Rise started before landing")
			if opening.intro_elapsed <= opening.INTRO_HOLD:
				require(island.camera.global_basis.z.dot(Vector3.UP) > .999999,"Overhead hold tilted")
			if opening.intro_elapsed > 1.5 and opening.intro_elapsed < 4.0:
				check_title_center()
				require(opening.title_group.modulate.a > .99,"Title plateau missing")
		else:
			require(not opening.title_layer.visible,"Title overlaps rising/dialogue")
		if opening.phase == opening.Phase.RISING and first_rise < 0:
			first_rise = frame
			boundary_distance = island.camera.position.distance_to(last_camera.origin)
			boundary_angle = island.camera.basis.get_rotation_quaternion().angle_to(last_camera.basis.get_rotation_quaternion())
			require(boundary_distance < .02 and boundary_angle < .002,"Camera popped at rise boundary")
		if opening.phase == opening.Phase.DIALOGUE and first_dialogue < 0:
			first_dialogue = frame
			require(animation_ends == 1,"Rise animation finish signal")
			require(island.hero.animation == &"idle_right","Dialogue must use standing frame")
		if frame % 24 == 0 or opening.phase != last_phase:
			samples.append({"frame":frame,"time":frame/24.0,"phase":opening.phase,"intro_time":opening.intro_elapsed,"hero_frame":island.hero.frame,"pitch":island.camera.rotation_degrees.x,"camera":str(island.camera.position),"title_alpha":opening.title_group.modulate.a})
		if frame in [0,36,72,108,144,172,195,220,250,280,312,400]:
			root.get_texture().get_image().save_png(OUT+"motion-%03d.png"%frame)
		require(root.get_texture().get_image().save_jpg(OUT+"frames/%04d.jpg"%frame,.94) == OK,"Movie frame save")
		last_camera = island.camera.transform
		last_phase = opening.phase
		if frame % 96 == 0: print("INTRO_MOTION_FRAME ",frame)
	Input.action_release("move_right")
	require(first_rise in range(169,174),"Intro duration")
	require(first_dialogue in range(303,313),"Rise and dialogue timing")
	require(island.coastal_life.elapsed > start_life + 18.0,"Environment stopped during cinematic")
	# Real confirmation input advances the two existing dialogue pages.
	key(KEY_SPACE)
	await wait_frames(80)
	require(island.opening.dialogue._page == 1,"Dialogue page advance")
	key(KEY_SPACE)
	await wait_frames(48)
	require(dialogue_ends == 1 and not island.opening.is_input_locked(),"Dialogue did not release input")
	require(island.hud.visible,"HUD not restored")
	Input.action_press("move_right")
	await wait_frames(12)
	Input.action_release("move_right")
	require(island.hero_x > island.HERO_START_X+.5,"Walking after intro")
	# Preserve a user's hidden HUD through a complete, normally finished replay.
	island.hud.hide()
	key(KEY_R)
	await wait_frames(390)
	key(KEY_SPACE)
	await wait_frames(80)
	key(KEY_SPACE)
	await wait_frames(48)
	require(not island.opening.is_input_locked() and not island.hud.visible,"Hidden HUD preference not restored")
	island.hud.show()
	# Replay from gameplay, descent, rise and active dialogue.
	for delay in [72,204,330]:
		key(KEY_R)
		await wait_frames(delay)
		key(KEY_R)
		await process_frame
		require(island.opening.phase == island.opening.Phase.ESTABLISHING,"Replay did not restart overhead")
		require(not island.opening.dialogue.is_dialogue_active(),"Replay left dialogue visible")
		require(island.hero.frame == 0 and not island.hero.is_playing(),"Replay lying frame")
	# Title remains centered when the window is resized.
	root.size = Vector2i(1600,900)
	await wait_frames(40)
	check_title_center()
	root.size = Vector2i(1280,720)
	var report := {"rendered_movie_frames":444,"fps":24,"duration_seconds":18.5,"exact_90_degree_first_frame":true,"held_lying_frame_until_descent":true,"title_centered_and_fades":true,"first_rising_frame":first_rise,"first_dialogue_frame":first_dialogue,"boundary_position_delta_m":boundary_distance,"boundary_angle_radians":boundary_angle,"input_lock_dialogue_unlock_replay":true,"resize_and_hidden_hud":true,"environment_continues":true,"samples":samples}
	FileAccess.open(OUT+"runtime-verification.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("OVERHEAD_OPENING_VERIFIED")
	quit(0)
