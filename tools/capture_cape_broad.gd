extends "res://tools/capture_pixel_bamboo.gd"
const OUT := "res://artifacts/cape-broad-notch-review/"
var camera_checks:Array=[]
func picture(label:String)->void:
	island._update_ground_contact()
	await settle(16)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	camera_checks.append({"label":label,"hero":str(island.hero.position),"camera":str(island.camera.position),"camera_pitch":island.camera.rotation_degrees.x,"presentation":island.hero_presentation.debug_state()})
	print("CAPE_SHOT ",phase," ",label)
func run_capture()->void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.hide();island.opening.set_process(false)
	control_time(island)
	freeze_material(island.get_node("PixelBambooAtmosphere/BambooInteriorMist").material,"fog")
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	position(island.HERO_START_X)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	island.camera.position=Vector3(-23,23,17);island.camera.look_at(Vector3(-23,1,-1.5));island.camera.fov=48
	island.hero_presentation.update(0,true)
	await picture("cape-overview")
	island.camera.position=Vector3(-24.5,30,-.5);island.camera.look_at(Vector3(-24.5,1,-.51));island.camera.fov=35
	await picture("cape-top")
	island.camera_effects.dof_blur_near_enabled=true;island.camera_effects.dof_blur_far_enabled=true
	for x in [island.HERO_START_X,-21.0,-15.0,-6.8,7.8]:
		position(x);await picture("walk-x%04.1f"%x)
	position(island.HERO_START_X)
	island.opening.enabled=true;island.skip_opening=false;island.opening.start();island.hero.pause()
	for frame in [0,38,65,85,102]:
		island.hero.frame=frame;island._update_camera(0,true)
		await picture("opening-%03d"%frame)
	island.opening._on_animation_finished()
	for i in 85:
		island.opening._process(1.0/60.0);island._update_camera(1.0/60.0)
	await picture("dialogue")
	island.opening.dialogue.hide();await picture("dialogue-clean")
	island.background_comparison.set_mode(1);await picture("sunset-dialogue-clean")
	island.background_comparison.set_mode(0)
	island.opening.dialogue.cancel_dialogue();island.opening._finish()
	for i in 110:
		island.opening._process(1.0/60.0);island._update_camera(1.0/60.0)
		if i in [30,65]:await picture("transition-%03d"%i)
	island.hud.hide();await picture("returned-walk")
	for i in 200:
		step_world(Vector2.RIGHT if i<130 else Vector2.LEFT,1.0/30.0)
		if i in [60,129,199]:await picture("movement-%03d"%i)
	FileAccess.open(OUT+phase+"-cameras.json",FileAccess.WRITE).store_string(JSON.stringify(camera_checks,"  "))
	quit(0)
