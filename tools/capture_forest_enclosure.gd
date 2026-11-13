extends "res://tools/capture_pixel_bamboo.gd"
const OUT := "res://artifacts/forest-enclosure-review/"
func picture(label: String) -> void:
	island._update_ground_contact()
	await settle(20)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	print("ENCLOSURE_SHOT ",phase," ",label)
func run_capture() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.hide()
	island.opening.set_process(false)
	control_time(island)
	freeze_material(island.get_node("PixelBambooAtmosphere/BambooInteriorMist").material,"fog")
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	var checks:Array=[]
	for x in [-15.2,-11.0,-6.8,-2.5,1.5,7.8,21.0]:
		position(x);await picture("x%04.1f"%x)
		checks.append({"hero_x":x,"hero":str(island.hero.position),"camera":str(island.camera.position),"fov_vertical":island.camera.fov})
	island.background_comparison.set_mode(1)
	position(-6.8);await picture("sunset-forest")
	position(7.8);await picture("sunset-bridge")
	island.background_comparison.set_mode(0)
	position(-6.8)
	set_time(14.0);await picture("mist-time14")
	set_time(1.0)
	var mist=island.get_node("PixelBambooAtmosphere/BambooInteriorMist")
	mist.visible=false;await picture("without-mist");mist.visible=true
	for mesh in island.find_children("ForestLightShaft_*","MeshInstance3D",true,false):mesh.hide()
	await picture("without-shafts")
	for mesh in island.find_children("ForestLightShaft_*","MeshInstance3D",true,false):mesh.show()
	for mesh in island.find_children("ForestForeground_*","MeshInstance3D",true,false):mesh.hide()
	await picture("without-foreground")
	for mesh in island.find_children("ForestForeground_*","MeshInstance3D",true,false):mesh.show()
	island.camera_effects.dof_blur_near_enabled=false
	island.camera_effects.dof_blur_far_enabled=false
	await picture("without-dof")
	position(-12.8);await picture("foreground-actor-crossing")
	island.camera_effects.dof_blur_near_enabled=true
	island.camera_effects.dof_blur_far_enabled=true
	island.opening.enabled=true
	island.skip_opening=false
	position(island.HERO_START_X)
	island.opening.start();island.hero.pause();island.hero.frame=0
	island._update_camera(0.0,true)
	await picture("opening-rest")
	island.hero.frame=102
	await picture("opening-rise-end")
	island.opening._on_animation_finished()
	for i in 100:
		island.opening._process(1.0/60.0)
		island._update_camera(1.0/60.0)
	await picture("opening-dialogue")
	island.opening.dialogue.cancel_dialogue()
	island.opening._finish()
	for i in 108:
		island.opening._process(1.0/60.0)
		island._update_camera(1.0/60.0)
		if i in [30,65]:await picture("transition-%03d"%i)
	await picture("opening-gameplay")
	var f:=FileAccess.open(OUT+phase+"-camera.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(checks,"  "))
	quit(0)
