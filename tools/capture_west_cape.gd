extends "res://tools/capture_background_comparison.gd"

const CAPE_REVIEW := "res://artifacts/west-cape-opening-review/"

func cape_shot(label: String) -> void:
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(CAPE_REVIEW+phase+"-"+label+".png") == OK)
	print("CAPE_SHOT ",label)

func capture_cape_motion() -> void:
	var samples: Array=[]
	var max_camera_step:=0.0
	for mode in 2:
		island.background_comparison.set_mode(mode)
		position(island.HERO_START_X)
		island.camera_facing=1.0
		island._update_camera(0.0,true)
		var folder: String=CAPE_REVIEW+VIEW_NAMES[mode]+"-frames"
		DirAccess.make_dir_recursive_absolute(folder)
		for frame in 360:
			var t:=float(frame)/20.0
			var direction:=Vector2.ZERO
			if t>=2.0 and t<7.0:direction=Vector2.RIGHT
			elif t>=9.0 and t<14.0:direction=Vector2.LEFT
			var prior: Vector3=island.camera.position
			step_world(direction,.05)
			max_camera_step=maxf(max_camera_step,island.camera.position.distance_to(prior))
			await settle(2)
			await RenderingServer.frame_post_draw
			assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94)==OK)
			if frame%20==0:samples.append({"mode":mode,"time":t,"hero_x":island.hero_x,"cape_weight":island.cape_opening,"camera":str(island.camera.position),"far_focus":island.camera_effects.dof_blur_far_distance})
			if frame%120==0:print("CAPE_FRAME ",mode," ",frame)
		assert(absf(island.hero_x-island.HERO_START_X)<.001)
		assert(island.cape_opening>.99)
	assert(max_camera_step<.8,str(max_camera_step))
	var file:=FileAccess.open(CAPE_REVIEW+"motion-verification.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"fps":20,"frames_each":360,"seconds_each":18,"modes":2,"max_camera_step_m":max_camera_step,"start_and_return_x":island.HERO_START_X,"samples":samples},"  "))

func run_capture() -> void:
	island = load("res://scenes/island.tscn").instantiate()
	root.add_child(island)
	current_scene = island
	island.set_process(false)
	island.hero.pause()
	island.hud.visible = false
	assert(island.hero_x==island.HERO_START_X)
	island._move_hero(Vector2.LEFT,1.0)
	assert(island.hero_x==island.HERO_START_X)
	position(-8.0)
	var reset:=InputEventKey.new()
	reset.keycode=KEY_R
	reset.pressed=true
	island._unhandled_key_input(reset)
	assert(island.hero_x==island.HERO_START_X and island.camera_facing==1.0)
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	position(island.HERO_START_X)
	if phase == "motion":
		await capture_cape_motion()
		quit(0)
		return
	if phase == "blockout":
		await cape_shot("before")
		var focus: Vector3 = island.hero.position+Vector3(-.45,1.1,0.0)
		island.camera.position = focus+Vector3(-1.6,10.0,20.0)
		island.camera.look_at(focus)
		island.camera.fov = 38.0
		island.camera_effects.dof_blur_far_distance=25.0
		island.camera_effects.dof_blur_far_transition=16.0
		island.camera_effects.dof_blur_near_distance=16.0
		island.camera_effects.dof_blur_amount=.09
		island.atmosphere.environment.ambient_light_energy=.22
		island.atmosphere.sun.light_color=Color("f2d4a2")
		island.atmosphere.sun.light_energy=1.8
		for water in island.atmosphere.water_materials:
			water.set_shader_parameter("deep_color",Color("07363e"))
			water.set_shader_parameter("reflected_zenith",Color("42636c"))
		await cape_shot("camera-light")
	else:
		for mode in 2:
			island.background_comparison.set_mode(mode)
			for point in [{"x":island.HERO_START_X,"label":"start"},{"x":-18.2,"label":"cape-path"},{"x":-15.0,"label":"transition"},{"x":-8.0,"label":"grove"},{"x":7.8,"label":"bridge"}]:
				position(point.x)
				await cape_shot(VIEW_NAMES[mode]+"-"+point.label)
	quit(0)
