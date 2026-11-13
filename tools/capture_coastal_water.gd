extends SceneTree

var island: Node3D
var phase := "pass1"
var controlled_materials: Array[ShaderMaterial] = []

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--phase="):
			phase = arg.trim_prefix("--phase=")
	call_deferred("run_capture")

func settle(frames: int) -> void:
	for i in frames:
		await process_frame

func control_time(node: Node) -> void:
	if node is MeshInstance3D:
		for surface in node.mesh.get_surface_count():
			var mat: Material = node.get_active_material(surface)
			if mat is ShaderMaterial and mat not in controlled_materials:
				var frozen := mat.shader.duplicate() as Shader
				var expression := RegEx.new()
				expression.compile("\\bTIME\\b")
				frozen.code = expression.sub(frozen.code, "review_time", true)
				frozen.code = frozen.code.replace("shader_type spatial;", "shader_type spatial;\nuniform float review_time = 1.0;")
				mat.shader = frozen
				controlled_materials.append(mat)
	for child in node.get_children():
		control_time(child)

func set_time(seconds: float) -> void:
	for mat in controlled_materials:
		mat.set_shader_parameter("review_time", seconds)

func save_view(label: String) -> void:
	await settle(6)
	await RenderingServer.frame_post_draw
	var path := "res://artifacts/water-light-review/" + phase + "-" + label + ".png"
	assert(root.get_texture().get_image().save_png(path) == OK)
	print("WATER_CAPTURE ", label)

func position(x: float) -> void:
	island.hero_x = x
	island.hero_path_offset = 0.0
	island._position_hero()
	island._update_camera(0.0, true)

func capture_movie() -> void:
	var folder := "res://artifacts/water-light-review/motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	position(-3.0)
	island.camera_effects.dof_blur_far_enabled = true
	island.camera_effects.dof_blur_near_enabled = true
	Input.action_press("move_right")
	var started := Time.get_ticks_msec()
	for frame in 540:
		var seconds := frame / 30.0
		set_time(seconds)
		if frame < 240:
			# Feed the existing input and movement code at a fixed capture timestep.
			island._process(1.0 / 30.0)
			island.hero.pause()
			island.hero.frame = int(seconds * 8.0) % island.hero.sprite_frames.get_frame_count(island.hero.animation)
		elif frame < 420:
			Input.action_release("move_right")
			island.hero.pause()
			island.camera_effects.dof_blur_far_enabled = false
			island.camera_effects.dof_blur_near_enabled = false
			var angle := lerpf(-0.38, 0.38, (frame - 240) / 179.0)
			island.camera.position = Vector3(10.0 + sin(angle) * 19.0, 16.5, cos(angle) * 19.0)
			island.camera.look_at(Vector3(10.0, -1.3, 0.0))
		else:
			if frame == 420:
				position(-6.8)
			var cover := lerpf(0.22, 0.90, smoothstep(0.0, 1.0, (frame - 420) / 119.0))
			island.atmosphere.apply(10.5, cover)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder + "/%04d.jpg" % frame, 0.94) == OK)
		if frame % 120 == 0:
			print("WATER_MOVIE_FRAME ", frame)
	Input.action_release("move_right")
	var output := FileAccess.open("res://artifacts/water-light-review/motion-verification.json", FileAccess.WRITE)
	output.store_string(JSON.stringify({"frames":540, "fps":30, "duration_seconds":18,
		"sections":["0-8s existing hero movement across bridge", "8-14s camera arc and moving water", "14-18s accelerated cloud cover transition"],
		"capture_seconds":(Time.get_ticks_msec()-started)/1000.0, "renderer":"Forward+ Vulkan", "size":str(root.size)}, "  "))
	print("WATER_MOVIE_COMPLETE")

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
		await capture_movie()
		quit(0)
		return
	position(-6.8)
	await save_view("midshot")
	position(7.8)
	await save_view("bridge")
	if "--diagnose" in OS.get_cmdline_user_args():
		var sea := island.find_child("Open_Sea", true, false) as MeshInstance3D
		var material := sea.material_override as ShaderMaterial
		var original := material.shader.code
		var variants := {
			"normal": "ALBEDO=vec3(0.0); EMISSION=world_normal*.5+.5; SPECULAR=0.0;",
			"diffuse": "EMISSION=vec3(0.0); SPECULAR=0.0;",
			"transmit": "ALBEDO=vec3(0.0); SPECULAR=0.0;",
			"specular": "ALBEDO=vec3(0.0); EMISSION=vec3(0.0);",
			"flat": "ALBEDO=vec3(.02,.12,.15); EMISSION=vec3(0.0); SPECULAR=0.0; NORMAL=normalize((VIEW_MATRIX*vec4(0.,1.,0.,0.)).xyz);",
		}
		for label in variants:
			material.shader.code = original.left(original.rfind("}")) + variants[label] + "\n}"
			await save_view(label)
		material.shader.code = original
		quit(0)
		return
	if "--quick" in OS.get_cmdline_user_args():
		quit(0)
		return
	position(20.0)
	await save_view("east")
	island.camera.position = Vector3(11.0, 17.0, 15.0)
	island.camera.look_at(Vector3(10.0, -1.0, 0.0))
	island.camera_effects.dof_blur_far_enabled = false
	island.camera_effects.dof_blur_near_enabled = false
	await save_view("water-detail")
	set_time(3.0)
	await save_view("water-detail-later")
	position(-6.8)
	island.atmosphere.apply(10.5, 0.9)
	await save_view("overcast")
	island.atmosphere.apply(14.5, 0.22)
	await save_view("afternoon")
	island.atmosphere.apply(island.daylight_hour, island.cloud_cover)
	print("WATER_VERIFIED ", controlled_materials.size(), " animated materials; weather updates bound water")
	quit(0)
