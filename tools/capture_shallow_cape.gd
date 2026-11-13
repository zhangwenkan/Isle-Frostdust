extends "res://tools/capture_cloud_water.gd"
const OUT := "res://artifacts/shallow-cape-review/"
func picture(label:String)->void:
	island._update_ground_contact()
	await settle(18)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	print("SHALLOW_CAPE_SHOT ",phase," ",label)
func run_capture()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false);island.hero.pause();island.hud.hide()
	control_time(island);set_time(2.0)
	island.opening.enabled=true;island.skip_opening=false;island.opening.start()
	for t in [1.8,7.2]:
		island.opening.intro_elapsed=t;island.opening._update_title();island._update_camera(0,true)
		await picture("intro-%03d"%int(t*10))
	island.opening._begin_rising();island.hero.pause()
	for f in [55,102]:
		island.hero.frame=f;island._update_camera(0,true);await picture("rise-%03d"%f)
	island.opening._on_animation_finished()
	island.opening.dialogue.cancel_dialogue();island.opening.phase=island.opening.Phase.COMPLETE
	for x in [-24.2,-21.0,-18.5]:
		position(x);await picture("walk-%04.1f"%x)
	position(-24.2)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	island.camera.position=Vector3(-30,6.8,15);island.camera.look_at(Vector3(-26.1,.6,-.1));island.camera.fov=43
	island.hero_presentation.update(0,true);await picture("cape-three-quarter")
	island.camera.position=Vector3(-26,3.3,18.5);island.camera.look_at(Vector3(-26,.35,0));island.camera.fov=40
	island.hero_presentation.update(0,true);await picture("cape-side")
	island.camera.position=Vector3(-25,21,8);island.camera.look_at(Vector3(-25,0,0));island.camera.fov=47
	await picture("cape-top")
	island.camera_effects.dof_blur_near_enabled=true;island.camera_effects.dof_blur_far_enabled=true
	position(-24.2);island.background_comparison.set_mode(1);await picture("sunset-walk")
	quit(0)
