extends "res://tools/capture_cloud_water.gd"

func shot(label:String)->void:
	island._update_ground_contact()
	await settle(12)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://artifacts/east-spring-review/"+phase+"-"+label+".png")==OK)
	print("SPRING_SHOT ",label)

func run_capture()->void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.opening.set_process(false)
	island.opening.enabled=false;island.skip_opening=true
	island.opening.dialogue.cancel_dialogue();island.opening.phase=island.opening.Phase.COMPLETE
	island.hero.animation="idle_right";island.hero.frame=0;island.hero.pause();island.hud.hide()
	control_time(island);set_time(2.0)
	var points=[20.0,23.7] if phase=="before" else [23.7,27.0,30.5,34.0]
	for x in points:
		position(x);await shot("x-%04.1f"%x)
	if phase!="before":
		position(34.0);set_time(3.0);await shot("water-later")
		island.background_comparison.set_mode(1);await shot("sunset")
		island.background_comparison.set_mode(0)
		island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
		position(34.0);await shot("no-dof")
		island.camera.position=Vector3(34,24,26);island.camera.look_at(Vector3(33,1,-4));island.camera.fov=55
		await shot("assembly")
	quit(0)
