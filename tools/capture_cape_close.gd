extends "res://tools/capture_background_comparison.gd"

const CAPE_REVIEW := "res://artifacts/cape-close-camera-review/"

func cape_shot(label: String) -> void:
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(CAPE_REVIEW+phase+"-"+label+".png") == OK)
	print("CAPE_SHOT ",label)

func capture_cape_motion() -> void:
	var samples: Array=[]
	var max_camera_step:=0.0
	var min_focus_margin:=100.0
	var sunlight: Vector3=island.atmosphere.sun.rotation_degrees
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
			var hero_depth: float=-island.camera.to_local(island.hero.global_position).z
			var focus_margin: float=minf(hero_depth-island.camera_effects.dof_blur_near_distance,island.camera_effects.dof_blur_far_distance-hero_depth)
			min_focus_margin=minf(min_focus_margin,focus_margin)
			assert(focus_margin>0.1,str(focus_margin))
			assert(island.atmosphere.sun.rotation_degrees.is_equal_approx(sunlight))
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
	file.store_string(JSON.stringify({"fps":20,"frames_each":360,"seconds_each":18,"modes":2,"max_camera_step_m":max_camera_step,"min_hero_focus_margin_m":min_focus_margin,"fixed_sun_rotation":str(sunlight),"start_and_return_x":island.HERO_START_X,"samples":samples},"  "))

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
	if phase == "tune":
		for setup in [
			{"label":"right-front","focus":Vector3(-4.3,1.1,-1.1),"offset":Vector3(5.0,7.0,9.0)},
			{"label":"closer","focus":Vector3(-3.3,1.3,-.8),"offset":Vector3(4.1,6.3,7.4)},
			{"label":"higher","focus":Vector3(-3.6,1.1,-1.1),"offset":Vector3(4.6,7.4,7.7)}]:
			var target: Vector3=island.hero.position+setup.focus
			island.camera.position=target+setup.offset
			island.camera.look_at(target)
			var hero_depth: float=-island.camera.to_local(island.hero.global_position).z
			island.camera_effects.dof_blur_near_distance=hero_depth-1.0
			island.camera_effects.dof_blur_near_transition=1.6
			island.camera_effects.dof_blur_far_distance=hero_depth+1.4
			island.camera_effects.dof_blur_far_transition=7.0
			await cape_shot(setup.label)
			print("CAPE_TUNE ",setup.label," depth=",hero_depth," feet=",island.camera.unproject_position(island.hero.global_position))
		quit(0)
		return
	if phase == "focus-check":
		await cape_shot("with-dof")
		var report: Dictionary={"camera":str(island.camera.position),"target":str(island.camera_focus),"sun_rotation":str(island.atmosphere.sun.rotation_degrees),"fov":island.camera.fov,"hero_depth":-island.camera.to_local(island.hero.global_position).z,"near_distance":island.camera_effects.dof_blur_near_distance,"far_distance":island.camera_effects.dof_blur_far_distance}
		var land: MeshInstance3D=island.find_child("Fish_West_Continuous_Land",true,false)
		var depths: Array[float]=[]
		for surface in land.mesh.get_surface_count():
			var vertices: PackedVector3Array=land.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
			for vertex in vertices:
				var world: Vector3=land.global_transform*vertex
				var screen: Vector2=island.camera.unproject_position(world)
				if screen.x>750 and screen.x<1280 and screen.y>620 and screen.y<720:
					depths.append(-island.camera.to_local(world).z)
		depths.sort()
		if not depths.is_empty():report["lower_terrain_depth_range"]=[depths.front(),depths.back()]
		var file:=FileAccess.open(CAPE_REVIEW+"focus-verification.json",FileAccess.WRITE)
		file.store_string(JSON.stringify(report,"  "))
		island.camera_effects.dof_blur_near_enabled=false
		island.camera_effects.dof_blur_far_enabled=false
		await cape_shot("without-dof")
		quit(0)
		return
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
