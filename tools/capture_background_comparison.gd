extends "res://tools/capture_living_coast.gd"

const COMPARISON_REVIEW := "res://artifacts/background-comparison-review/"
const VIEW_NAMES := ["original", "sunset"]

func picture(label: String) -> void:
	await settle(30)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(COMPARISON_REVIEW+label+".png") == OK)
	print("COMPARISON_SHOT ",label)

func click_button() -> void:
	var button: Button = island.background_comparison.button
	var point := button.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = point
	Input.parse_input_event(motion)
	for pressed in [true,false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.position = point
		event.pressed = pressed
		Input.parse_input_event(event)
		await settle(2)

func capture_cloudsea_motion() -> void:
	var folder := "res://artifacts/sunset-layered-cloudsea-review/motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	island.background_comparison.set_mode(1)
	island.hud.visible = false
	position(-2.5)
	for frame in 240:
		var seconds := float(frame)/20.0
		var direction := Vector2.RIGHT if seconds < 7.0 else (Vector2.LEFT if seconds >= 9.0 else Vector2.ZERO)
		step_world(direction,1.0/20.0)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.9) == OK)
	print("CLOUDSEA_MOTION_VERIFIED 240 frames, 12 seconds, walk/pause/return")

func capture_atmosphere_motion() -> void:
	var folder := "res://artifacts/sunset-atmosphere-blend-review/motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	island.background_comparison.set_mode(1)
	island.hud.visible = false
	position(7.8)
	# Keep the camera fixed for 18 seconds so actual sky/cloud motion is visible.
	for frame in 360:
		var seconds := float(frame)/20.0
		step_world(Vector2.ZERO,1.0/20.0)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94) == OK)
		if frame%120 == 0:
			assert(root.get_texture().get_image().save_png(folder+"/time-%02d.png"%int(seconds)) == OK)
	print("ATMOSPHERE_MOTION_VERIFIED 360 frames, 18 seconds, fixed camera")

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	position(7.8)
	var comparison = island.background_comparison
	if phase == "procedural-tune":
		island.hud.visible = false
		for mode in 2:
			comparison.set_mode(mode)
			position(7.8)
			set_time(1.0)
			await picture("procedural-%d-bridge"%mode)
			island.camera.look_at(island.camera.position+Vector3(0,.16,-1))
			for seconds in [1.0,19.0,61.0]:
				set_time(seconds)
				await picture("procedural-%d-sky-%d"%[mode,int(seconds)])
		quit(0)
		return
	if phase == "atmosphere-motion":
		await capture_atmosphere_motion()
		quit(0)
		return
	if "--movie" in OS.get_cmdline_user_args():
		await capture_cloudsea_motion()
		quit(0)
		return
	if phase == "edge-diagnose":
		comparison.set_mode(1)
		island.hud.visible = false
		await picture("edge-current")
		var fog_volume := island.atmosphere.get_node("MountainCloudSea") as FogVolume
		fog_volume.visible = false
		await picture("edge-no-volume")
		for material in island.atmosphere.water_materials:
			material.set_shader_parameter("sunset_haze",0.0)
		await picture("edge-no-volume-no-water-haze")
		fog_volume.visible = true
		await picture("edge-no-water-haze")
		quit(0)
		return
	var original_hero: Vector3 = island.hero.position
	var original_camera: Transform3D = island.camera.transform
	var sunlight: float = island.atmosphere.sun.light_energy
	var water: ShaderMaterial = island.atmosphere.water_materials[0]
	var water_values: Dictionary = {}
	for key in ["deep_color","shallow_color","reflected_horizon","reflected_zenith","wave_strength","sun_elevation_sine"]:
		water_values[key] = water.get_shader_parameter(key)
	var checks: Array = []
	assert(comparison.LABELS.size() == 2)
	assert(not island.camera.has_node("DistantMountainInkContours"))
	for index in VIEW_NAMES.size():
		assert(comparison.mode == index)
		assert(island.hero.position == original_hero)
		assert(island.camera.transform == original_camera)
		assert(island.atmosphere.sun.light_energy == sunlight)
		for material in island.atmosphere.water_materials:
			assert(material.get_shader_parameter("sunset_haze") == float(index))
		assert(comparison.original_mountains[0].visible == (index == 0))
		assert(comparison.ink_mountains.visible == (index == 1))
		for key in water_values:
			assert(water.get_shader_parameter(key) == water_values[key])
		await picture(VIEW_NAMES[index]+"-ui")
		island.hud.visible = false
		await picture(VIEW_NAMES[index]+"-bridge")
		island.hud.visible = true
		checks.append({"mode":index,"label":comparison.button.text,"camera_unchanged":true,"water_parameters_unchanged":true,"visible_ridges":14})
		await click_button()
	assert(comparison.mode == 0)
	island.hud.visible = false
	await picture("original-return")
	position(-6.8)
	await picture("restored-forest")
	position(23.5)
	await picture("restored-east")
	comparison.set_mode(1)
	for point in [{"label":"sunset-forest","x":-6.8},{"label":"sunset-east","x":23.5}]:
		position(point.x)
		await picture(point.label)
	position(7.8)
	set_time(19.0)
	await picture("sunset-bridge-later")
	set_time(1.0)
	comparison.set_mode(0)
	# F6 works while the HUD is hidden, and repeated toggles don't accumulate nodes/materials.
	var node_count := island.get_child_count()
	for index in 4:
		var key := InputEventKey.new()
		key.keycode = KEY_F6
		key.pressed = true
		Input.parse_input_event(key)
		await settle(2)
		assert(comparison.mode == (index+1)%VIEW_NAMES.size())
	assert(island.get_child_count() == node_count)
	position(2.0)
	for frame in 150:
		step_world(Vector2.RIGHT,1.0/30.0)
		if frame%40 == 0:comparison.cycle()
		await settle(1)
	assert(island.hero_x > 19.9)
	comparison.set_mode(0)
	island._move_hero(Vector2.ZERO,0)
	var file := FileAccess.open(COMPARISON_REVIEW+"runtime-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"modes":checks,"mouse_cycle":true,"f6_cycle_with_hidden_hud":true,"wrap_to_original":true,"switch_while_walking":true,"end_hero_x":island.hero_x,"no_node_accumulation":true},"  "))
	print("BACKGROUND_COMPARISON_VERIFIED")
	quit(0)
