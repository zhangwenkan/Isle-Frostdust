extends "res://tools/capture_background_comparison.gd"

const SKY_REVIEW := "res://artifacts/procedural-sky-review/"
var review_samples: Array = []

func measure_runtime() -> void:
	position(7.8)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	var viewport_rid := root.get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(viewport_rid,true)
	var results: Array = []
	for mode in 2:
		island.background_comparison.set_mode(mode)
		await settle(90)
		var frame_ms: Array[float] = []
		var gpu_ms: Array[float] = []
		var previous := Time.get_ticks_usec()
		for frame in 180:
			await process_frame
			var now := Time.get_ticks_usec()
			frame_ms.append(float(now-previous)/1000.0)
			previous = now
			gpu_ms.append(RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid))
		frame_ms.sort()
		gpu_ms.sort()
		results.append({"mode":VIEW_NAMES[mode],"frame_ms_median":frame_ms[90],"frame_ms_p95":frame_ms[171],"viewport_gpu_ms_median":gpu_ms[90]})
	var file := FileAccess.open(SKY_REVIEW+"runtime-timing.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"size":str(root.size),"frames_per_mode":180,"vsync":false,"results":results},"  "))
	print("SKY_RUNTIME_TIMING ",JSON.stringify(results))

func picture(label: String) -> void:
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(SKY_REVIEW+phase+"-"+label+".png") == OK)
	print("SKY_SHOT ",label)

func capture_sequence_for_mode(mode: int) -> void:
	var label: String = VIEW_NAMES[mode]
	var folder := SKY_REVIEW+label+"-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	island.background_comparison.set_mode(mode)
	position(7.8)
	island.coastal_life.elapsed = 0.0
	set_time(0.0)
	await settle(30)
	var fixed_camera: Transform3D = island.camera.transform
	for frame in 720:
		var seconds := float(frame)/20.0
		var direction := Vector2.ZERO
		# 0-18 s: fixed bridge camera; 18-36 s: walk, pause, return.
		if frame == 360:
			position(-6.8)
		if seconds >= 18.0 and seconds < 26.4:
			direction = Vector2.RIGHT
		elif seconds >= 28.0:
			direction = Vector2.LEFT
		step_world(direction,1.0/20.0)
		if frame < 360:
			island.camera.transform = fixed_camera
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.95) == OK)
		if frame%120 == 0:
			review_samples.append({"mode":label,"time":seconds,"hero_x":island.hero_x,"camera":str(island.camera.transform)})
			print("SKY_MOTION ",label," ",frame,"/720")
	print("SKY_MOTION_COMPLETE ",label)

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hud.visible = false
	if phase == "performance":
		island.set_process(true)
		await measure_runtime()
		quit(0)
		return
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	if phase == "motion":
		for mode in 2:
			await capture_sequence_for_mode(mode)
		var file := FileAccess.open(SKY_REVIEW+"motion-verification.json",FileAccess.WRITE)
		file.store_string(JSON.stringify({"fps":20,"frames_per_mode":720,"seconds_per_mode":36,"time_scale":1.0,"fixed_camera_seconds":18,"walk_pause_return_seconds":18,"samples":review_samples},"  "))
	else:
		for mode in 2:
			island.background_comparison.set_mode(mode)
			for seconds in [1.0,13.0,25.0,61.0,121.0]:
				position(7.8)
				set_time(seconds)
				await picture("%s-bridge-%03d"%[VIEW_NAMES[mode],int(seconds)])
				if seconds in [1.0,25.0,61.0]:
					island.camera.look_at(island.camera.position+Vector3(0,.16,-1))
					await picture("%s-sky-%03d"%[VIEW_NAMES[mode],int(seconds)])
			for point in [{"label":"forest","x":-6.8},{"label":"east","x":23.5}]:
				position(point.x)
				set_time(1.0)
				await picture(VIEW_NAMES[mode]+"-"+point.label)
	print("PROCEDURAL_SKY_COMPLETE ",phase)
	quit(0)
