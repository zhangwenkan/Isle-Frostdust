extends "res://tools/capture_living_coast.gd"

const CLIFF := "res://artifacts/cliff-form-review/"

func shot(label: String) -> void:
	await settle(22)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(CLIFF+phase+"-"+label+".png")==OK)
	print("CLIFF_SHOT ",label)

func record_cliffs() -> void:
	var folder := CLIFF+phase+"-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	position(-12.0)
	set_time(0.0)
	await settle(32)
	for frame in 900:
		var t := float(frame)/30.0
		var direction := Vector2.ZERO
		if t>=2.0 and t<11.0:
			direction = Vector2.RIGHT
		elif t>=14.0 and t<21.0:
			direction = Vector2.LEFT
		step_world(direction,1.0/30.0)
		if t>=24.0:
			island.camera_effects.dof_blur_near_enabled = false
			island.camera_effects.dof_blur_far_enabled = false
			var u := smoothstep(0.0,1.0,(t-24.0)/6.0)
			island.camera.position = Vector3(8.0-u*8.0,5.0,18.0)
			island.camera.look_at(Vector3(-6.0,0.65,2.5))
		await settle(2)
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94)==OK)
		if frame%150==0:print("CLIFF_FRAME ",frame," hero_x=",island.hero_x)
	var file := FileAccess.open(CLIFF+phase+"-motion-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"frames":900,"fps":30,"duration_seconds":30,"size":str(root.size),"time_scale":1.0,"sections":["0-2s forest idle","2-11s walk west to east","11-14s east idle","14-21s return west","21-24s west idle","24-30s cliff side inspection"]},"  "))
	print("CLIFF_MOVIE_COMPLETE")

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
		await record_cliffs()
		quit(0)
		return
	set_time(1.0)
	position(-6.8)
	await settle(40)
	await shot("forest")
	position(7.8)
	await shot("bridge")
	position(20.0)
	await shot("east")
	position(-6.8)
	island.atmosphere.apply(10.5,0.90)
	await shot("overcast")
	island.atmosphere.apply(10.5,0.22)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	island.camera.position = Vector3(-8.0,4.4,19.0)
	island.camera.look_at(Vector3(-8.0,0.65,2.5))
	await shot("cliff-detail")
	island.camera.position = Vector3(-4.7,2.2,7.0)
	island.camera.look_at(Vector3(-4.7,0.3,3.0))
	await shot("rock-sample")
	island.camera.position = Vector3(9.8,3.4,10.0)
	island.camera.look_at(Vector3(3.3,-0.3,1.1))
	await shot("bridge-abutment")
	island.camera.position = Vector3(9.2,6.8,9.5)
	island.camera.look_at(Vector3(9.2,-3.9,0.7))
	await shot("underwater")
	quit(0)
