extends "res://tools/capture_background_comparison.gd"

const STONE_REVIEW := "res://artifacts/stone-spatial-review/"

func picture(label: String) -> void:
	await settle(25)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(STONE_REVIEW+phase+"-"+label+".png") == OK)
	print("STONE_SHOT ",label)

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hud.visible = false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	if phase == "motion":
		await record_walk()
		quit(0)
		return
	for mode in 2:
		island.background_comparison.set_mode(mode)
		for p in [{"x":-17.0,"label":"entry"},{"x":-10.7,"label":"west-rocks"},{"x":-6.8,"label":"forest"},{"x":-3.4,"label":"exit"},{"x":7.8,"label":"bridge"}]:
			position(p.x)
			await picture(VIEW_NAMES[mode]+"-"+p.label)
	island.background_comparison.set_mode(0)
	position(-10.7)
	island.camera_effects.dof_blur_near_enabled=false
	island.camera_effects.dof_blur_far_enabled=false
	island.lens.set_shader_parameter("enabled",false)
	island.camera.position=Vector3(-11.0,7.8,5.0)
	island.camera.look_at(Vector3(-11.0,5.0,-2.0))
	await picture("main-detail")
	quit(0)

func record_walk() -> void:
	var samples: Array=[]
	for mode in 2:
		island.background_comparison.set_mode(mode)
		var folder: String=STONE_REVIEW+VIEW_NAMES[mode]+"-frames"
		DirAccess.make_dir_recursive_absolute(folder)
		position(-17.0)
		for frame in 440:
			var t:=float(frame)/20.0
			var direction:=Vector2.ZERO
			if t>=2.0 and t<8.5:direction=Vector2.RIGHT
			elif t>=12.0 and t<18.5:direction=Vector2.LEFT
			step_world(direction,.05)
			await settle(2)
			await RenderingServer.frame_post_draw
			assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94)==OK)
			if frame%20==0:samples.append({"mode":mode,"time":t,"hero_x":island.hero_x})
			if frame%120==0:print("STONE_FRAME ",mode," ",frame)
	var file:=FileAccess.open(STONE_REVIEW+"motion-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"fps":20,"frames_per_mode":440,"seconds_per_mode":22,"time_scale":1,"sections":["idle","walk right","idle","return","idle"],"samples":samples},"  "))
