extends "res://tools/capture_cloud_water.gd"
const OUT := "res://artifacts/reference-shore-fit/"
func picture(label:String)->void:
	island._update_ground_contact()
	await settle(14)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	print("COAST_SHOT ",phase," ",label)
func run_capture()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hero.pause();island.hud.hide()
	control_time(island)
	set_time(2.0)
	island.opening.enabled=true;island.skip_opening=false;island.opening.start()
	for t in [1.8,4.4,7.2]:
		island.opening.intro_elapsed=t;island.opening._update_title();island._update_camera(0,true)
		await picture("intro-%03d"%int(t*10))
	island.opening._begin_rising();island.hero.pause();island.hero.frame=102;island.opening._on_animation_finished()
	island.opening.dialogue.cancel_dialogue();island.opening.phase=island.opening.Phase.COMPLETE
	for x in [-24.2,-20.0,-16.0,-13.0,-10.0,-6.8,-2.5,1.5,4.1,7.8]:
		position(x);await picture("walk-%04.1f"%x)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	island.camera.position=Vector3(-14,27,24);island.camera.look_at(Vector3(-12,1,-3));island.camera.fov=53
	await picture("overview")
	island.camera.position=Vector3(-16,7,20);island.camera.look_at(Vector3(-15,0,1));island.camera.fov=46
	await picture("cliff-close")
	island.camera.position=Vector3(-13,10,39);island.camera.look_at(Vector3(-13,0,0));island.camera.fov=48
	await picture("cliff-wide")
	island.camera_effects.dof_blur_near_enabled=true;island.camera_effects.dof_blur_far_enabled=true
	position(-6.8);island.background_comparison.set_mode(1);await picture("sunset-forest")
	position(3.0);await picture("sunset-bridge-entry")
	quit(0)
