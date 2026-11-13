extends "res://tools/capture_living_coast.gd"

const CINEMA := "res://artifacts/cinematic-coast-review/"

func shot(label: String) -> void:
	await settle(18)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(CINEMA+phase+"-"+label+".png")==OK)
	print("CINEMA_SHOT ",label)

func record_coast() -> void:
	var folder := CINEMA+phase+"-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	var records: Array = []
	var start_clock := Time.get_ticks_msec()
	for frame in 1410:
		var t := float(frame)/30.0
		var direction := Vector2.ZERO
		if t < 39.0:
			if (t >= 3.0 and t < 7.0) or (t >= 13.0 and t < 17.5) or t >= 35.0:
				direction = Vector2.RIGHT
			elif t >= 21.0 and t < 29.0:
				direction = Vector2.LEFT
			step_world(direction,1.0/30.0)
		else:
			island.coastal_life.advance(1.0/30.0,island.hero_x)
			set_time(island.coastal_life.elapsed)
			island.camera_effects.dof_blur_near_enabled = false
			island.camera_effects.dof_blur_far_enabled = false
			island.camera.position = Vector3(9.2,6.8,9.5)
			island.camera.look_at(Vector3(9.2,-3.9,0.7))
		if frame % 30 == 0:
			var fish_positions: Array = []
			for data in island.coastal_life.swimmers:
				fish_positions.append({"name":data.node.name,"position":str(data.node.position),"yaw":data.node.rotation.y})
			records.append({"seconds":t,"hero_x":island.hero_x,"camera":str(island.camera.position),"fov":island.camera.fov,"life":island.coastal_life.debug_state(),"fish":fish_positions})
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,0.94)==OK)
		if frame % 180 == 0:
			print("CINEMA_FRAME ",frame," x=",island.hero_x)
	assert(island.coastal_life.flock_count==1)
	assert(island.coastal_life.swimmers.size()==4)
	var file := FileAccess.open(CINEMA+phase+"-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"frames":1410,"fps":30,"duration_seconds":47,"size":str(root.size),"time_scale":1.0,"flock_events":island.coastal_life.flock_count,"sections":["0-3s forest idle","3-7s walk onto bridge","7-13s bridge idle","13-17.5s walk to east grove","17.5-21s east idle","21-29s return west","29-35s west idle","35-39s repeat approach","39-47s water detail"],"capture_wall_seconds":(Time.get_ticks_msec()-start_clock)/1000.0,"timeline":records},"  "))
	print("CINEMA_SEQUENCE_COMPLETE 1410")

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
	if "--movie" in OS.get_cmdline_user_args():
		position(-6.8)
		set_time(0.0)
		await settle(40)
		await record_coast()
		quit(0)
		return
	set_time(1.0)
	position(-6.8)
	await settle(40)
	await shot("forest")
	position(7.8)
	await shot("bridge")
	if "--quick" in OS.get_cmdline_user_args():
		quit(0)
		return
	position(20.0)
	await shot("east")
	position(7.8)
	island.atmosphere.apply(10.5,0.90)
	await shot("overcast")
	island.atmosphere.apply(10.5,0.22)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	island.camera.position = Vector3(9.2,6.8,9.5)
	island.camera.look_at(Vector3(9.2,-3.9,0.7))
	await shot("underwater-detail")
	island.find_child("Open_Sea",true,false).visible=false
	await shot("underwater-assets")
	print("CINEMA_SWIMMERS ",island.coastal_life.swimmers.size())
	quit(0)
