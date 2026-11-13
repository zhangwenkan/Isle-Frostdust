extends "res://tools/capture_background_comparison.gd"
const VALLEY_REVIEW := "res://artifacts/bamboo-valley-review/"

func valley_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(VALLEY_REVIEW+phase+"-"+label+".png")==OK)
	print("VALLEY_SHOT ",phase," ",label)

func run_capture() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene=island
	island.set_process(false)
	island.hero.pause()
	island.hud.visible=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	if phase=="motion":
		position(-14.5)
		var folder:=VALLEY_REVIEW+"motion-frames"
		DirAccess.make_dir_recursive_absolute(folder)
		var samples:Array=[]
		var smallest_margin:=99999.0
		for frame in 360:
			var seconds:=float(frame)/20.0
			var direction:=Vector2.ZERO
			if seconds>=1.0 and seconds<7.3:direction=Vector2.RIGHT
			elif seconds>=9.3 and seconds<15.6:direction=Vector2.LEFT
			step_world(direction,.05)
			island._update_ground_contact()
			var point:Vector2=island.camera.unproject_position(island.hero.global_position+Vector3(0,1.1,0))
			smallest_margin=minf(smallest_margin,minf(minf(point.x,1280-point.x),minf(point.y,720-point.y)))
			await settle(2)
			await RenderingServer.frame_post_draw
			assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94)==OK)
			if frame%20==0:samples.append({"seconds":seconds,"hero_x":island.hero_x,"camera":str(island.camera.global_position)})
		assert(absf(island.hero_x+14.5)<.002)
		assert(smallest_margin>40)
		var output:=FileAccess.open(VALLEY_REVIEW+"motion-verification.json",FileAccess.WRITE)
		output.store_string(JSON.stringify({"frames":360,"fps":20,"duration":18,"returned_to_start":true,"minimum_actor_center_margin_px":smallest_margin,"samples":samples},"  "))
		quit(0)
		return
	for x in [-20.7,-15.0,-11.0,-6.8,-2.5,1.5,4.2,7.8]:
		position(x)
		await valley_shot("x%04.1f"%x)
	if phase!="before":
		island.background_comparison.set_mode(1)
		for x in [-6.8,1.5,7.8]:
			position(x)
			await valley_shot("sunset-x%04.1f"%x)
		island.background_comparison.set_mode(0)
		position(-6.8)
		island.camera_effects.dof_blur_near_enabled=false
		island.camera_effects.dof_blur_far_enabled=false
		await valley_shot("without-dof")
		island.camera.position=Vector3(-3,17,8)
		island.camera.look_at(Vector3(-6.8,6.5,-10))
		await valley_shot("valley-detail")
	quit(0)
