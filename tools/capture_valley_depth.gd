extends "res://tools/capture_background_comparison.gd"
const DEPTH_REVIEW := "res://artifacts/valley-depth-review/"
func depth_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(DEPTH_REVIEW+phase+"-"+label+".png")==OK)
	print("DEPTH_SHOT ",phase," ",label)

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
	for x in [island.HERO_START_X,-14.0,-12.8,-11.0,-6.8,-2.5,1.5,7.8]:
		position(x)
		await depth_shot("x%04.1f"%x)
		checks.append({"hero_x":x,"actor_depth":-island.camera.to_local(island.hero.global_position).z,"far_focus":island.camera_effects.dof_blur_far_distance,"far_transition":island.camera_effects.dof_blur_far_transition,"camera":str(island.camera.position),"pitch":island.camera.rotation_degrees.x})
	island.background_comparison.set_mode(1)
	position(-6.8);await depth_shot("sunset-forest")
	position(7.8);await depth_shot("sunset-bridge")
	island.background_comparison.set_mode(0)
	position(-6.8)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	await depth_shot("without-dof")
	position(island.HERO_START_X)
	island.hero.sprite_frames=load("res://assets/characters/rest_rise_right/color_matched/rest_rise_color_matched.tres")
	island.hero.animation=&"rest_rise_right";island.hero.frame=0
	await depth_shot("lying")
	var f:=FileAccess.open(DEPTH_REVIEW+phase+"-camera.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(checks,"  "))
	quit(0)
