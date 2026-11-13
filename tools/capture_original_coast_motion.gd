extends "res://tools/capture_cloud_water.gd"
const OUT := "res://artifacts/original-shore-review/"
func run_capture() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hud.hide()
	assert(not island.opening.is_input_locked())
	control_time(island)
	freeze_material(island.atmosphere.sky_cloud_material,"sky")
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	position(island.HERO_START_X)
	var folder:=OUT+"review-motion-frames"
	DirAccess.make_dir_recursive_absolute(folder)
	var timeline:Array=[]
	var max_support_error:=0.0
	await settle(24)
	for frame in 480:
		var t:=float(frame)/24.0
		var right:bool=t>=1.0 and t<8.0
		var left:bool=t>=10.0 and t<17.0
		Input.action_release("move_right");Input.action_release("move_left")
		if right:Input.action_press("move_right")
		if left:Input.action_press("move_left")
		island._process(1.0/24.0)
		island.hero.pause()
		island.hero.frame=int(t*8.0)%island.hero.sprite_frames.get_frame_count(island.hero.animation)
		set_time(t)
		var support:Dictionary=island.hero_presentation.surface.sample(island.hero.position.x,island.hero.position.z)
		assert(not support.is_empty())
		var error:float=absf(island.hero.position.y-float(support.height)-.04)
		max_support_error=maxf(max_support_error,error)
		assert(error<.002)
		await settle(2);await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94)==OK)
		if frame%24==0:timeline.append({"time":t,"hero_x":island.hero_x,"animation":str(island.hero.animation)})
		if frame%120==0:print("ORIGINAL_COAST_MOTION ",frame)
	Input.action_release("move_left");Input.action_release("move_right")
	assert(absf(island.hero_x-island.HERO_START_X)<.01)
	FileAccess.open(OUT+"motion-verification.json",FileAccess.WRITE).store_string(JSON.stringify({"frames":480,"fps":24,"duration":20,"renderer":"Vulkan Forward+","size":str(root.size),"capture":"fixed-step actual scene, movement, camera and environment; not a performance benchmark","max_ground_support_error_m":max_support_error,"returned_to_start":true,"timeline":timeline},"  "))
	print("ORIGINAL_COAST_MOTION_COMPLETE")
	quit(0)
