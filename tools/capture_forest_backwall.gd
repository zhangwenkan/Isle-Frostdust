extends "res://tools/capture_pixel_bamboo.gd"
const OUT := "res://artifacts/forest-backwall-review/"
var camera_rays:Array=[]
func picture(label:String)->void:
	island._update_ground_contact()
	await settle(20)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUT+phase+"-"+label+".png")==OK)
	print("BACKWALL_SHOT ",phase," ",label)
func record_rays(x:float)->void:
	var rays:Array=[]
	for j in 12:
		for i in 33:
			var point:=Vector2(1280*(.05+.90*i/32.0),720*(.04+.55*j/11.0))
			var origin:Vector3=island.camera.project_ray_origin(point)
			var direction:Vector3=island.camera.project_ray_normal(point)
			rays.append({"screen":[point.x,point.y],"origin":[origin.x,origin.y,origin.z],"direction":[direction.x,direction.y,direction.z]})
	camera_rays.append({"hero_x":x,"rays":rays})
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
	for x in [-24.2,-18.0,-15.0,-13.0,-10.0,-6.8,-3.0,-.5,2.5,7.8]:
		position(x);await picture("x%04.1f"%x)
		if x>=-15 and x<=-.5:record_rays(x)
	island.background_comparison.set_mode(1)
	position(-6.8);await picture("sunset-forest")
	position(7.8);await picture("sunset-bridge")
	island.background_comparison.set_mode(0)
	position(-13.0)
	var motion_samples:=0
	for direction in [Vector2.RIGHT,Vector2.ZERO,Vector2.LEFT]:
		for i in 60:
			step_world(direction,1.0/30.0)
			var support:Dictionary=island.hero_presentation.surface.sample(island.hero.position.x,island.hero.position.z)
			assert(not support.is_empty())
			assert(absf(float(support.height)-1.86)<.01)
			motion_samples+=1
		await picture("movement-%d"%motion_samples)
	assert(absf(island.hero_x+13.0)<.01)
	FileAccess.open(OUT+phase+"-movement.json",FileAccess.WRITE).store_string(JSON.stringify({"samples":motion_samples,"seconds":6,"right_idle_left":true,"supported":true,"returned_x":island.hero_x,"note":"Stepped simulation with three static captures; not a recorded playback."},"  "))
	position(-6.8);set_time(14.0);await picture("wind-time14")
	set_time(1.0)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	await picture("without-dof")
	island.camera.position=Vector3(-11,32,30);island.camera.look_at(Vector3(-11,3,-5));island.camera.fov=52
	await picture("overview")
	island.camera_effects.dof_blur_near_enabled=true;island.camera_effects.dof_blur_far_enabled=true
	island.opening.enabled=true;island.skip_opening=false;position(island.HERO_START_X)
	island.opening.start();island.hero.pause();island.hero.frame=0;island._update_camera(0,true)
	await picture("opening-rest")
	FileAccess.open(OUT+phase+"-camera-rays.json",FileAccess.WRITE).store_string(JSON.stringify(camera_rays))
	quit(0)
