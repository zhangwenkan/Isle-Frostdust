extends "res://tools/capture_background_comparison.gd"

const INK_REVIEW := "res://artifacts/colored-ink-sample-review/"

func picture(label: String) -> void:
	await settle(25)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(INK_REVIEW+phase+"-"+label+".png") == OK)
	print("INK_SAMPLE_SHOT ",label)

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
		await record_sample()
		quit(0)
		return
	for mode in 2:
		island.background_comparison.set_mode(mode)
		for p in [{"x":-10.7,"label":"west-rocks"},{"x":-6.8,"label":"forest"},{"x":-3.4,"label":"east-rocks"},{"x":7.8,"label":"bridge"},{"x":23.5,"label":"east-end"}]:
			position(p.x)
			await picture(VIEW_NAMES[mode]+"-"+p.label)
	island.background_comparison.set_mode(0)
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled = false
	island.camera_effects.dof_blur_far_enabled = false
	island.lens.set_shader_parameter("enabled",false)
	await picture("forest-sharp")
	island.camera.position = Vector3(-4.6,4.9,6.0)
	island.camera.look_at(Vector3(-4.6,3.55,-1.4))
	await picture("stone-detail")
	position(-6.8)
	island.atmosphere.apply(10.5,.75)
	await picture("overcast")
	print("INK_SAMPLE_COMPLETE")
	quit(0)

func record_sample() -> void:
	var samples: Array = []
	for mode in 2:
		island.background_comparison.set_mode(mode)
		var folder: String = INK_REVIEW+VIEW_NAMES[mode]+"-frames"
		DirAccess.make_dir_recursive_absolute(folder)
		position(-10.7)
		for frame in 360:
			var t := float(frame)/20.0
			var direction := Vector2.ZERO
			if t>=3.0 and t<6.0:direction=Vector2.RIGHT
			elif t>=10.0 and t<13.0:direction=Vector2.LEFT
			step_world(direction,.05)
			await settle(2)
			await RenderingServer.frame_post_draw
			assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.95)==OK)
			if frame%60==0:samples.append({"mode":mode,"time":t,"hero_x":island.hero_x})
			if frame%120==0:print("INK_SAMPLE_FRAME ",mode," ",frame)
	var file := FileAccess.open(INK_REVIEW+"motion-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"fps":20,"frames_per_mode":360,"seconds_per_mode":18,"time_scale":1,"sections":["idle","walk right","idle","return","idle"],"samples":samples},"  "))
