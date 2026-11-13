extends "res://tools/capture_cloud_water.gd"
## Runtime contact, animation switching and stills for the front-only trial.
const OUT := "res://artifacts/q-front-integration-review/"
var failures: Array[String] = []
var loop_count := 0
var report: Dictionary = {}

func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)
		push_error(message)

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	island._unhandled_key_input(event)

func pose(animation: StringName, frame := 0) -> void:
	island.hero.animation = animation
	island.hero.set_frame_and_progress(frame, 0)
	island.hero.pause()
	island.hero_presentation.update(0.0, true)
	island._update_ground_contact()

func shot(label: String) -> void:
	await settle(12)
	await RenderingServer.frame_post_draw
	check(root.get_texture().get_image().save_png(OUT + label + ".png") == OK, "Capture " + label)

func run_capture() -> void:
	root.size = Vector2i(1280, 720)
	island = load("res://scenes/island.tscn").instantiate()
	island.skip_opening = true
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hud.hide()
	var original: SpriteFrames = load("res://assets/characters/green_three_walk/swordsman_walk.tres")
	var active: SpriteFrames = island.hero.sprite_frames
	check(not original.has_animation(&"walk_down_q"), "Original SpriteFrames was not mutated")
	for animation in original.get_animation_names():
		check(active.get_frame_count(animation) == original.get_frame_count(animation), "Original frame count " + animation)
		check(active.get_animation_speed(animation) == original.get_animation_speed(animation), "Original speed " + animation)
		for frame in original.get_frame_count(animation):
			check(active.get_frame_texture(animation, frame) == original.get_frame_texture(animation, frame), "Original texture preserved")
	check(active.get_frame_count(&"walk_down_q") == 23, "23 Q walk frames")
	check(is_equal_approx(active.get_animation_speed(&"walk_down_q"), 31.2), "Q walk runs 30 percent faster")
	check(is_equal_approx(island.hero.speed_scale, 1.0), "No global animation acceleration")
	var presenter: RefCounted = island.hero_presentation
	var min_clearance := INF
	var samples := 0
	for x in [-6.8, 4.3, 9.5, 14.4, 20.0]:
		for offset in [-.45, 0.0, .45]:
			position(x)
			island.hero_path_offset = offset
			island._position_hero()
			island._update_camera(0, true)
			for animation in [&"walk_down_q", &"idle_down_q"]:
				for frame in active.get_frame_count(animation):
					pose(animation, frame)
					check(presenter.last_frame_data.get("feet", []).size() == 2, "Two matching foot contacts")
					check(presenter.material.get_shader_parameter("has_volume"), "New sprite uses matching normal map")
					check(not presenter.material.get_shader_parameter("has_surface"), "Old standing map not applied to Q face")
					for point: Array in presenter.last_frame_data.sole:
						var px: float = (point[0] - 256) * island.hero.pixel_size
						var py: float = (724 - point[1]) * island.hero.pixel_size
						py = presenter.grounded_local_y(px, py)
						var world: Vector3 = island.hero.position + island.hero.basis.x * px + island.hero.basis.y * py + Vector3.UP * presenter.lift
						min_clearance = minf(min_clearance, world.y - float(presenter.ground(world.x, world.z).height))
						samples += 1
	check(min_clearance >= -.005, "Sole outlines stay above imported surfaces within 5mm")
	report["contacts"] = {"samples": samples, "minimum_clearance_m": min_clearance}
	position(-6.8)
	island.hero_facing = Vector2.DOWN
	island._move_hero(Vector2.ZERO, 0.0)
	check(island.hero.animation == &"idle_down_q", "Stop uses Q idle")
	key(KEY_F8)
	check(island.hero.animation == &"walk_down_q" and island.hero.is_playing(), "F8 previews Q walk")
	key(KEY_F7)
	check(island.hero.animation == &"walk_down" and island.hero.is_playing(), "F7 switches to old walk")
	key(KEY_F7)
	check(island.hero.animation == &"walk_down_q", "F7 returns to Q walk")
	island._move_hero(Vector2.DOWN, 1.0/60.0)
	check(not island.hero_front_preview and island.hero.animation == &"walk_down_q", "Movement exits preview and walks with new front")
	island._move_hero(Vector2.ZERO, 0.0)
	check(island.hero.animation == &"idle_down_q", "Release returns to Q standing")
	for direction in [Vector2.RIGHT, Vector2.LEFT, Vector2.UP]:
		island._move_hero(direction, 1.0/60.0)
		check(island.hero.animation in [&"walk_right", &"walk_up"], "Other directions use original sprites")
	# Cross-atlas and new/old switches bind the correct color and normal together.
	for state in [[&"walk_down_q",15],[&"walk_down_q",16],[&"idle_down_q",0],[&"walk_down",23],[&"idle_down",0]]:
		pose(state[0], state[1])
		var texture: Texture2D = active.get_frame_texture(state[0], state[1])
		var base: Texture2D = texture.atlas if texture is AtlasTexture else texture
		check(presenter.material.get_shader_parameter("color_atlas") == base, "Color atlas changes synchronously")
		check(presenter.material.get_shader_parameter("volume_atlas") == presenter.normal_atlases[base.resource_path.get_file().get_basename()], "Normal atlas matches current sprite")
	# Play at the real engine clock; do not simulate frames by stepping the index.
	loop_count = 0
	island.hero.animation_looped.connect(func(): loop_count += 1)
	island.hero.play(&"walk_down_q")
	await create_timer(1.65).timeout
	check(loop_count >= 2, "Real playback completes at least two fast cycles")
	report["playback"] = {"fps": 31.2, "observed_loops_in_1_65s": loop_count, "cycle_seconds":23.0/31.2}
	pose(&"idle_down_q")
	# Restore opening frames and return through its own callback.
	island.opening.enabled = true
	island.opening.start()
	check(is_equal_approx(island.hero.speed_scale, 1.0), "Opening speed remains unchanged")
	island.hero.pause()
	island.hero.frame = 102
	island.opening._on_animation_finished()
	check(island.hero.sprite_frames == active and active.has_animation(&"walk_down_q"), "Opening restores combined walk resource")
	island.opening.dialogue.cancel_dialogue()
	island.opening._finish()
	island.skip_opening = true
	island.hud.hide()
	position(-6.8)
	pose(&"idle_down")
	await shot("old-front-grove")
	pose(&"idle_down_q")
	await shot("q-front-grove")
	pose(&"walk_down_q", 3)
	await shot("q-walk-grove")
	island.camera.position = island.hero.position + Vector3.UP * 1.28 + island.camera.global_basis.z * 7.8
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	await shot("q-walk-detail")
	position(9.5)
	pose(&"walk_down_q", 16)
	await shot("q-walk-bridge")
	report["passed"] = failures.is_empty()
	report["failures"] = failures
	report["video_recorded"] = false
	var file := FileAccess.open(OUT + "verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	print("Q_FRONT_VERIFY ", JSON.stringify(report))
	quit(0 if failures.is_empty() else 1)
