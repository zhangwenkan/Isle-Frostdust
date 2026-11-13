extends "res://tools/capture_background_comparison.gd"
const PIXEL_REVIEW := "res://artifacts/pixel-bamboo-west-review/"
func pixel_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(PIXEL_REVIEW+phase+"-"+label+".png")==OK)
	print("PIXEL_SHOT ",phase," ",label)
func run_capture() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.visible=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	var checks:Array=[]
	for x in [island.HERO_START_X,-11.0,-6.8,-2.5,1.5,7.8,21.0]:
		position(x)
		await pixel_shot("x%04.1f"%x)
		checks.append({"hero_x":x,"hero":str(island.hero.position),"camera":str(island.camera.position),"pitch":island.camera.rotation_degrees.x})
	island.background_comparison.set_mode(1)
	position(-6.8);await pixel_shot("sunset-forest")
	position(1.5);await pixel_shot("sunset-mouth")
	island.background_comparison.set_mode(0)
	if phase!="before":
		position(-6.8)
		set_time(4.0);await pixel_shot("wind-t4")
		set_time(1.0)
		island.camera_effects.dof_blur_near_enabled=false
		island.camera_effects.dof_blur_far_enabled=false
		await pixel_shot("without-dof")
	var f:=FileAccess.open(PIXEL_REVIEW+phase+"-camera.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(checks,"  "))
	quit(0)
