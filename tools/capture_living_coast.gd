extends "res://tools/capture_cloud_water.gd"

const LIVING_REVIEW := "res://artifacts/living-coast-review/"
var timeline: Array = []
var event_samples: Array[Vector3] = []

func step_world(direction: Vector2, seconds: float) -> void:
	island._move_hero(direction,seconds)
	island._update_camera(seconds)
	island.coastal_life.advance(seconds,island.hero_x)
	set_time(island.coastal_life.elapsed)
	island.hero.pause()
	island.hero.frame = int(island.coastal_life.elapsed * 8.0) % island.hero.sprite_frames.get_frame_count(island.hero.animation)

func shot(label: String) -> void:
	await settle(20)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(LIVING_REVIEW+phase+"-"+label+".png") == OK)
	print("LIVING_SHOT ",label)

func capture_sequence() -> void:
	var folder := LIVING_REVIEW + phase + "-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	var total := 1170
	if "--quick" in OS.get_cmdline_user_args():
		total = 540
	for frame in total:
		var t := float(frame)/30.0
		var direction := Vector2.ZERO
		if (t >= 3.0 and t < 7.0) or (t >= 13.0 and t < 17.5) or t >= 35.0:
			direction = Vector2.RIGHT
		elif t >= 21.0 and t < 29.0:
			direction = Vector2.LEFT
		step_world(direction,1.0/30.0)
		if frame % 30 == 0:
			timeline.append({"time":t,"hero_x":island.hero_x,"life":island.coastal_life.debug_state()})
		if island.coastal_life.gulls[3].node.visible:
			event_samples.append(island.coastal_life.gulls[3].node.position)
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,0.92)==OK)
		if frame % 180 == 0:
			print("LIVING_FRAME ",frame," x=",island.hero_x," events=",island.coastal_life.flock_count)
	assert(island.coastal_life.flock_count==1)
	assert(event_samples.size()>60)
	var z_min := 100.0
	var z_max := -1000.0
	for p in event_samples:
		z_min = minf(z_min,p.z)
		z_max = maxf(z_max,p.z)
	assert(z_max-z_min>30.0)
	var file := FileAccess.open(LIVING_REVIEW+phase+"-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"frames":total,"fps":30,"duration":float(total)/30.0,"flock_events":island.coastal_life.flock_count,"flock_z_range":[z_min,z_max],"timeline":timeline,"size":str(root.size)},"  "))
	print("LIVING_SEQUENCE_COMPLETE ",total)

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
	position(-6.8)
	set_time(0.0)
	await settle(40)
	if "--movie" in OS.get_cmdline_user_args():
		await capture_sequence()
		quit(0)
		return
	await shot("idle-forest")
	for frame in 140:
		step_world(Vector2.RIGHT,1.0/30.0)
	await shot("flock-departure")
	for frame in 120:
		step_world(Vector2.ZERO,1.0/30.0)
	await shot("bridge-paused")
	position(20.0)
	await shot("east")
	island.atmosphere.apply(10.5,0.9)
	await shot("overcast")
	island.atmosphere.apply(10.5,0.22)
	# Inspect authored gull and joint positions at a close, still camera.
	var bird: Node3D = island.coastal_life.gulls[0].node
	var focus: Vector3 = bird.global_position
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	island.camera.position = focus+Vector3(1.4,0.8,1.9)
	island.camera.look_at(focus)
	await shot("bird-detail")
	quit(0)
