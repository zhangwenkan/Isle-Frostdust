extends "res://tools/capture_cloud_water.gd"
const OUT := "res://artifacts/hd2d-upright-review/"

func run_capture() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	island.skip_opening=true
	root.add_child(island)
	current_scene=island
	island.set_process(false)
	island.hero.pause()
	island.hud.hide()
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	set_time(1.0)
	var details: Array=[]
	for x in [-13.0,5.2]:
		for item in [["idle_right",0,false],["idle_right",0,true],["idle_down",0,false],["walk_right",10,false],["walk_up",15,false],["walk_down",10,false]]:
			island.hero.animation=StringName(item[0])
			island.hero.frame=item[1]
			island.hero.flip_h=item[2]
			position(x)
			island._update_ground_contact()
			await settle(6)
			await RenderingServer.frame_post_draw
			var label: String=("steep" if x<0 else "bridge")+"-"+item[0]+("-left" if item[2] else "")
			var full: Image=root.get_texture().get_image()
			full.save_png(OUT+"detail-"+label+".png")
			var foot: Vector2=island.camera.unproject_position(island.hero.position+Vector3.UP*island.hero_presentation.lift)
			full.get_region(Rect2i(int(foot.x)-110,int(foot.y)-220,220,280)).save_png(OUT+"crop-"+label+".png")
			details.append({"label":label,"root_lift_m":island.hero_presentation.lift,"foot_offsets":Array(island.hero_presentation.contact_curve)})
	position(5.2)
	var started:=Time.get_ticks_usec()
	for i in 120:
		island.hero_x=5.2+i*.025
		island._position_hero()
		island._update_camera(1.0/60.0)
		island._update_ground_contact()
	var moving_us: float=(Time.get_ticks_usec()-started)/120.0
	started=Time.get_ticks_usec()
	for i in 120:island.hero_presentation.update(1.0/60.0)
	var idle_us: float=(Time.get_ticks_usec()-started)/120.0
	island.background_comparison.set_mode(1)
	for point in [{"x":-6.8,"label":"grove"},{"x":9.5,"label":"bridge"}]:
		island.hero.animation=&"idle_right"
		island.hero.frame=0
		island.hero.flip_h=false
		position(point.x)
		island._update_ground_contact()
		await settle(10)
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(OUT+"after-sunset-"+point.label+".png")
	var file:=FileAccess.open(OUT+"detail-checks.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"poses":details,"average_moving_camera_contact_us":moving_us,"average_stationary_contact_us":idle_us,"video_recorded":false},"  "))
	print("UPRIGHT_DETAILS moving_us=",moving_us," idle_us=",idle_us)
	quit(0)
