extends "res://tools/capture_cloud_water.gd"
const OUT := "res://artifacts/ink-bridge-review/"
func shot(label:String) -> void:
	island._update_ground_contact()
	await settle(20)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	print("BRIDGE_STATIC ",phase," ",label)
func run_capture() -> void:
	root.size=Vector2i(1280,720)
	island=load("res://scenes/island.tscn").instantiate();island.skip_opening=true
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.hide()
	island.hero.animation=&"idle_right";island.hero.flip_h=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	for mode in [0,1]:
		island.background_comparison.set_mode(mode)
		for point in [{"x":3.4,"label":"west-entry"},{"x":9.5,"label":"middle"},{"x":15.5,"label":"east-entry"}]:
			position(point.x);await shot(("original-" if mode==0 else "sunset-")+point.label)
	island.background_comparison.set_mode(0)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	position(9.5);await shot("no-dof")
	island.camera.position=Vector3(8.7,4.8,6.0)
	island.camera.look_at(Vector3(8.5,1.15,.25))
	island.hero.visible=false
	await shot("detail")
	island.atmosphere.apply(11.2,.9)
	await shot("detail-overcast")
	quit(0)
