extends SceneTree

var island: Node3D
var phase := "pass1"
var materials: Dictionary = {}
var report: Dictionary = {}
var freeze_sources: Dictionary = {}

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--phase="):
			phase = arg.trim_prefix("--phase=")
	call_deferred("run_capture")

func settle(frames: int) -> void:
	for i in frames:
		await process_frame

func inspect(node: Node) -> void:
	if node is MeshInstance3D:
		for surface in node.mesh.get_surface_count():
			var material: Material = node.get_active_material(surface)
			if material is StandardMaterial3D:
				materials[material.resource_name] = {
					"normal_enabled": material.normal_enabled,
					"normal_texture": material.normal_texture.resource_path if material.normal_texture else "",
					"albedo_texture": material.albedo_texture.resource_path if material.albedo_texture else "",
					"normal_scale": material.normal_scale,
					"roughness": material.roughness,
				}
			if material is ShaderMaterial:
				var source: Shader = material.shader
				if source and not freeze_sources.has(material):
					freeze_sources[material] = source
					var frozen := source.duplicate() as Shader
					var expression := RegEx.new()
					expression.compile("\\bTIME\\b")
					frozen.code = expression.sub(source.code, "1.0", true)
					material.shader = frozen
	for child in node.get_children():
		inspect(child)

func capture_view(label: String, x: float) -> void:
	island.hero_x = x
	island._position_hero()
	island._update_camera(0.0, true)
	await settle(35)
	await RenderingServer.frame_post_draw
	var picture := root.get_texture().get_image()
	var path := "res://artifacts/palm-style-review/" + phase + "-" + label + ".png"
	assert(picture.save_png(path) == OK)
	print("PALM_CAPTURE ", label, " size=", picture.get_size())

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	if "--no-shadow" in OS.get_cmdline_user_args():
		island.atmosphere.sun.shadow_enabled = false
	island.set_process(false)
	island.hero.pause()
	island.hero.frame = 0
	island.hero.flip_h = false
	island.hud.visible = false
	inspect(island)
	await settle(50)
	await capture_view("midshot", -6.8)
	if "--quick" in OS.get_cmdline_user_args():
		quit(0)
		return
	await capture_view("bridge", 5.5)
	await capture_view("cliff", -17.0)
	await capture_view("east", 20.0)
	var offset: Vector3 = island.camera_offset
	island.camera_offset = Vector3(0.0, 4.0, 12.4)
	await capture_view("detail", -9.0)
	island.camera_offset = offset
	island.atmosphere.apply(10.5, 0.9)
	var sea := island.find_child("Open_Sea", true, false) as MeshInstance3D
	island.atmosphere.configure_water(sea.material_override)
	await capture_view("overcast", -6.8)
	island.atmosphere.apply(island.daylight_hour, island.cloud_cover)
	island.atmosphere.configure_water(sea.material_override)
	# Restore live shader time, then exercise actual movement across both bridge landings.
	for material in freeze_sources:
		material.shader = freeze_sources[material]
	island.hero_x = 3.2
	island._position_hero()
	island._update_camera(0.0, true)
	island.set_process(true)
	Input.action_press("move_right")
	var begin := Time.get_ticks_msec()
	var frame_count := 0
	var last := Vector3.ZERO
	var max_step := 0.0
	while island.hero_x < 16.0 and Time.get_ticks_msec() - begin < 20000:
		await process_frame
		frame_count += 1
		if frame_count > 1:
			max_step = maxf(max_step, last.distance_to(island.hero.position))
		last = island.hero.position
	Input.action_release("move_right")
	assert(island.hero_x >= 16.0, "Traversal did not reach the east landing")
	island.set_process(false)
	await capture_view("motion-end", island.hero_x)
	report = {"phase": phase, "materials": materials, "motion_frames": frame_count,
		"motion_seconds": (Time.get_ticks_msec() - begin) / 1000.0,
		"maximum_frame_step_m": max_step, "landed_x": island.hero_x,
		"view_size": str(root.size), "daylight_hour": island.daylight_hour, "cloud_cover": island.cloud_cover}
	var file := FileAccess.open("res://artifacts/palm-style-review/" + phase + "-verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	print("PALM_VERIFIED ", frame_count, " motion frames; landed x=", island.hero_x)
	quit(0)
