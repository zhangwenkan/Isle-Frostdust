extends "res://tools/capture_coastal_water.gd"

const REVIEW := "res://artifacts/mountain-depth-review/"

func save_view(label: String) -> void:
	await settle(12)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(REVIEW + phase + "-" + label + ".png") == OK)
	print("MOUNTAIN_CAPTURE ", label)

func record_traversal() -> void:
	var folder := REVIEW + "motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	position(-17.0)
	Input.action_press("move_right")
	for frame in 420:
		set_time(frame / 30.0)
		island._process(1.0 / 30.0)
		island.hero.pause()
		island.hero.frame = int(frame / 4.0) % island.hero.sprite_frames.get_frame_count(island.hero.animation)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder + "/%04d.jpg" % frame, 0.94) == OK)
		if frame % 100 == 0:
			print("MOUNTAIN_MOTION ",frame," x=",island.hero_x)
	Input.action_release("move_right")
	assert(island.hero_x > 23.0)
	var output := FileAccess.open(REVIEW + "motion-verification.json",FileAccess.WRITE)
	output.store_string(JSON.stringify({"frames":420,"fps":30,"duration_seconds":14,"landed_x":island.hero_x,"size":str(root.size),"renderer":"Vulkan Forward+","static_shots_size":"2560x1440"},"  "))
	print("MOUNTAIN_MOTION_COMPLETE")

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
	assert(island.find_child("Depth_Forest_Shore",true,false) == null)
	assert(island.find_children("Depth_Bamboo_Back*","MeshInstance3D",true,false).is_empty())
	assert(island.find_child("Depth_Mountain_Ranges",true,false) != null)
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
	island.camera.position = Vector3(4.0,9.0,-12.0)
	island.camera.look_at(Vector3(4.0,3.0,-55.0))
	await save_view("mountain-detail")
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled = true
	island.camera_effects.dof_blur_far_enabled = true
	island.atmosphere.apply(10.5,0.9)
	await save_view("overcast")
	island.atmosphere.apply(14.5,0.22)
	await save_view("afternoon")
	quit(0)
