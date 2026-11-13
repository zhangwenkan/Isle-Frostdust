extends "res://tools/capture_living_coast.gd"

const SPACE_REVIEW := "res://artifacts/foreground-space-review/"

func shot(label: String) -> void:
	await settle(20)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(SPACE_REVIEW+phase+"-"+label+".png")==OK)
	print("SPACE_SHOT ",label)

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hud.visible = false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.atmosphere.sky_cloud_material,"sky")
	set_time(1.0)
	if "--movie" in OS.get_cmdline_user_args():
		await record_space()
		quit(0)
		return
	for point in [{"x":-16.0,"label":"west-entry"},{"x":-6.8,"label":"forest"},{"x":1.5,"label":"landing"},{"x":7.8,"label":"bridge"},{"x":20.0,"label":"east"},{"x":23.5,"label":"east-end"}]:
		position(point.x)
		await shot(point.label)
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	island.lens.set_shader_parameter("enabled",false)
	await shot("forest-sharp")
	island.camera.position = Vector3(-8.0,4.4,19.0)
	island.camera.look_at(Vector3(-8.0,0.65,2.5))
	await shot("cliff-detail")
	position(20.0)
	await shot("east-sharp")
	island.camera_effects.dof_blur_near_enabled = true
	island.camera_effects.dof_blur_far_enabled = true
	island.lens.set_shader_parameter("enabled",true)
	island.atmosphere.apply(10.5,0.90)
	await shot("overcast")
	quit(0)

func record_space() -> void:
	var folder := SPACE_REVIEW+"motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	position(-17.0)
	set_time(0.0)
	await settle(32)
	var samples: Array = []
	var previous_camera: Vector3 = island.camera.position
	var max_step := 0.0
	for frame in 1080:
		var t := float(frame)/30.0
		var direction := Vector2.ZERO
		if (t>=2.0 and t<8.5) or (t>=11.5 and t<16.0):
			direction = Vector2.RIGHT
		elif t>=19.0 and t<30.0:
			direction = Vector2.LEFT
		step_world(direction,1.0/30.0)
		max_step = maxf(max_step,island.camera.position.distance_to(previous_camera))
		previous_camera = island.camera.position
		if frame%30==0:
			samples.append({"time":t,"hero_x":island.hero_x,"camera":str(island.camera.position),"opening":island.camera_opening,"life":island.coastal_life.debug_state()})
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.93)==OK)
		if frame%180==0:print("SPACE_FRAME ",frame," x=",island.hero_x)
	assert(max_step<0.3)
	var file := FileAccess.open(SPACE_REVIEW+"motion-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"frames":1080,"fps":30,"seconds":36,"size":str(root.size),"max_camera_step":max_step,"timeline":samples,"sections":["west idle","walk to bridge","bridge idle","walk east","east idle","return west","west idle"]},"  "))
	print("SPACE_MOVIE_COMPLETE")
