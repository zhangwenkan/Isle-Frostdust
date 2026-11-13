extends "res://tools/capture_coastal_water.gd"

const REVIEW := "res://artifacts/misty-peaks-review/"

func save_view(label: String) -> void:
	await settle(12)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(REVIEW + phase + "-" + label + ".png") == OK)
	print("MIST_CAPTURE ", label)

func record_traversal() -> void:
	var folder := REVIEW + "motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	position(-17.0)
	for frame in 420:
		set_time(frame / 30.0)
		# Exercise the game's movement and follow camera without OS focus clearing Input.
		island._move_hero(Vector2.RIGHT, 1.0 / 30.0)
		island._update_camera(1.0 / 30.0)
		island.hero.pause()
		island.hero.frame = int(frame / 4.0) % island.hero.sprite_frames.get_frame_count(island.hero.animation)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder + "/%04d.jpg" % frame, 0.94) == OK)
		if frame % 100 == 0:
			print("MIST_MOTION ",frame," x=",island.hero_x)
	if island.hero_x < 23.0:
		push_error("MIST_MOTION_FAILED: did not reach the eastern shore")
		quit(1)
		return
	var output := FileAccess.open(REVIEW + "motion-verification.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"frames":420,"fps":30,"duration_seconds":14,"landed_x":island.hero_x,"size":str(root.size),"renderer":"Vulkan Forward+","movement":"Existing _move_hero and _update_camera at fixed 30 fps"},"  "))
	print("MIST_MOTION_COMPLETE")

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hero.frame = 0
	island.hud.visible = false
	control_time(island)
	# Freeze the volumetric cloud clock alongside the water and foliage for comparisons.
	var fog_material: ShaderMaterial = island.atmosphere.mountain_cloud_material
	var fog_shader := fog_material.shader.duplicate() as Shader
	var clock_expression := RegEx.new()
	clock_expression.compile("\\bTIME\\b")
	fog_shader.code = clock_expression.sub(fog_shader.code, "review_time", true)
	fog_shader.code = fog_shader.code.replace("shader_type fog;", "shader_type fog;\nuniform float review_time = 1.0;")
	fog_material.shader = fog_shader
	controlled_materials.append(fog_material)
	var sky_material: ShaderMaterial = island.atmosphere.sky_cloud_material
	var sky_shader := sky_material.shader.duplicate() as Shader
	sky_shader.code = clock_expression.sub(sky_shader.code, "review_time", true)
	sky_shader.code = sky_shader.code.replace("shader_type sky;", "shader_type sky;\nuniform float review_time = 1.0;")
	sky_material.shader = sky_shader
	controlled_materials.append(sky_material)
	await settle(35)
	assert(island.find_child("Depth_Forest_Shore",true,false) == null)
	assert(island.find_children("Depth_Bamboo_Back*","MeshInstance3D",true,false).is_empty())
	assert(island.find_child("Mist_Peak_Near_02",true,false) != null)
	if "--movie" in OS.get_cmdline_user_args():
		await record_traversal()
		quit(0)
		return
	for point in [{"label":"midshot","x":-6.8},{"label":"west","x":-15.0},{"label":"bridge","x":7.8},{"label":"east","x":20.0}]:
		position(point.x)
		await save_view(point.label)
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	await save_view("no-dof")
	# Inspect the authored mountain at a closer normal perspective without post blur.
	island.camera.position = Vector3(4.0,13.0,-35.0)
	island.camera.look_at(Vector3(4.0,8.0,-110.0))
	await save_view("mountain-detail")
	island.atmosphere.environment.volumetric_fog_enabled = false
	await save_view("mountain-no-clouds")
	island.atmosphere.environment.volumetric_fog_enabled = true
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled = true
	island.camera_effects.dof_blur_far_enabled = true
	island.atmosphere.apply(10.5,0.9)
	await save_view("overcast")
	island.atmosphere.apply(14.5,0.22)
	await save_view("afternoon")
	quit(0)
