extends "res://tools/capture_background_comparison.gd"
const CAMP_REVIEW := "res://artifacts/cape-road-alignment-review/"

func camp_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(CAMP_REVIEW+phase+"-"+label+".png")==OK)
	print("CAMP_SHOT ",label)

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
	position(island.HERO_START_X)
	if phase=="motion":
		var folder:=CAMP_REVIEW+"motion-frames"
		DirAccess.make_dir_recursive_absolute(folder)
		var samples: Array=[]
		for frame in 240:
			var t:=float(frame)/20.0
			var direction:=Vector2.ZERO
			if t>=1.0 and t<4.0:direction=Vector2.RIGHT
			elif t>=6.0 and t<9.0:direction=Vector2.LEFT
			step_world(direction,.05)
			island._update_ground_contact()
			await settle(2)
			await RenderingServer.frame_post_draw
			assert(root.get_texture().get_image().save_jpg(folder+"/%04d.jpg"%frame,.94)==OK)
			if frame%20==0:samples.append({"time":t,"x":island.hero_x,"position":str(island.hero.position),"shadow":str(island.contact_shadow.global_position)})
		assert(absf(island.hero_x-island.HERO_START_X)<.001)
		var file:=FileAccess.open(CAMP_REVIEW+"motion-verification.json",FileAccess.WRITE)
		file.store_string(JSON.stringify({"frames":240,"fps":20,"seconds":12,"returned_to_start":true,"samples":samples},"  "))
		quit(0)
		return
	if phase=="route-check":
		var routes: Array=[]
		for x in [-22.0,-20.7,-19.5,-18.5,-17.0,-15.0,-12.5]:
			position(maxf(x,island.HERO_START_X))
			var a:=Vector3(x-.3,island._height(x-.3,island._path_z(x-.3)),island._path_z(x-.3))
			var b:=Vector3(x+.3,island._height(x+.3,island._path_z(x+.3)),island._path_z(x+.3))
			var delta: Vector2=island.camera.unproject_position(b)-island.camera.unproject_position(a)
			routes.append({"x":x,"screen_angle_degrees":rad_to_deg(delta.angle()),"center_z":island._path_z(x)})
		position(island.HERO_START_X)
		island.hero.sprite_frames=load("res://assets/characters/rest_rise_right/rest_rise_chin.tres")
		island.hero.animation=&"rest_rise_right"
		island.hero.frame=0
		island._update_ground_contact()
		var file:=FileAccess.open(CAMP_REVIEW+"route-projection.json",FileAccess.WRITE)
		file.store_string(JSON.stringify({"samples":routes,"shadow_local_aabb":str(island.contact_shadow.mesh.get_aabb()),"shadow_transform":str(island.contact_shadow.global_transform),"shadow_uv":str(island.contact_shadow.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV])},"  "))
		quit(0)
		return
	if phase=="probe":
		var probes: Array=JSON.parse_string(FileAccess.get_file_as_string(CAMP_REVIEW+"site-probes.json"))
		for item in probes:
			var point:=Vector3(item.godot[0],item.godot[1],item.godot[2])
			item["screen"]=str(island.camera.unproject_position(point))
			item["distance_from_hero_xz"]=Vector2(point.x-island.hero.position.x,point.z-island.hero.position.z).length()
		print("SITE_PROJECTIONS ",JSON.stringify(probes))
		var file:=FileAccess.open(CAMP_REVIEW+"site-projections.json",FileAccess.WRITE)
		file.store_string(JSON.stringify(probes,"  "))
		quit(0)
		return
	for mode in 2:
		island.background_comparison.set_mode(mode)
		position(island.HERO_START_X)
		await camp_shot(VIEW_NAMES[mode]+"-standing")
		var frames: SpriteFrames=island.hero.sprite_frames
		island.hero.sprite_frames=load("res://assets/characters/rest_rise_right/rest_rise_chin.tres")
		island.hero.animation=&"rest_rise_right"
		for frame in [0,50,70]:
			island.hero.frame=frame
			await camp_shot(VIEW_NAMES[mode]+"-rise-%03d"%frame)
		island.hero.sprite_frames=frames
		island._set_hero_animation(&"idle_right",false)
		position(-17.5)
		await camp_shot(VIEW_NAMES[mode]+"-walk-away")
	position(island.HERO_START_X)
	island.background_comparison.set_mode(0)
	island.camera_effects.dof_blur_near_enabled=false
	island.camera_effects.dof_blur_far_enabled=false
	await camp_shot("without-dof")
	var center:=Vector3(-23.0,island._height(-23.0,-.06),-.06)
	island.hero.hide()
	island.contact_shadow.hide()
	island.camera.position=center+Vector3(1.6,2.3,3.2)
	island.camera.look_at(center)
	await camp_shot("asset-detail")
	quit(0)
