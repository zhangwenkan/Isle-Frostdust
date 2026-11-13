extends "res://tools/capture_background_comparison.gd"
const FOREST_REVIEW := "res://artifacts/forest-visibility-review/"
func forest_shot(label: String) -> void:
	island._update_ground_contact()
	await settle(24)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(FOREST_REVIEW+phase+"-"+label+".png")==OK)
	print("FOREST_SHOT ",phase," ",label)
func run_capture() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.visible=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	for node in island.find_children("ForestVisibility*","MeshInstance3D",true,false):
		if "Bamboo" in node.name:continue
		for surface in node.mesh.get_surface_count():
			var material=node.get_active_material(surface)
			print("FOREST_MATERIAL ",node.name," ",surface," ",material.shader.resource_path if material is ShaderMaterial else material.resource_name)
	var checks:Array=[]
	if phase=="diagnose":
		position(-6.8)
		await forest_shot("normal")
		island.find_child("Open_Sea",true,false).visible=false
		await forest_shot("no-sea")
		for node in island.find_children("ForestVisibility*","MeshInstance3D",true,false):
			if "Bamboo" in node.name:continue
			for surface in node.mesh.get_surface_count():
				var mat=node.get_active_material(surface)
				print("MATERIAL_CODE ",node.name," ",mat.shader.code.left(400) if mat is ShaderMaterial else "standard")
		quit(0)
		return
	for x in [island.HERO_START_X,-12.8,-11.0,-6.8,-2.5,1.5,7.8]:
		position(x)
		await forest_shot("x%04.1f"%x)
		checks.append({"hero_x":x,"camera":str(island.camera.position),"pitch":island.camera.rotation_degrees.x})
	island.background_comparison.set_mode(1)
	position(-6.8);await forest_shot("sunset-forest")
	position(7.8);await forest_shot("sunset-bridge")
	island.background_comparison.set_mode(0)
	position(1.5)
	for sample_time in [1.0,2.5,4.0]:
		for node in island.find_children("ForestVisibility_Creek*","MeshInstance3D",true,false):
			for surface in node.mesh.get_surface_count():
				var material=node.get_active_material(surface) as ShaderMaterial
				if material:material.set_shader_parameter("review_time",sample_time)
		await forest_shot("waterfall-time-%.1f"%sample_time)
	set_time(1.0)
	position(-6.8)
	var creek=island.find_child("ForestVisibility_Creek",true,false) as MeshInstance3D
	var creek_mat=creek.get_active_material(0) as ShaderMaterial
	for sample_time in [1.0,2.5,4.0]:
		creek_mat.set_shader_parameter("review_time",sample_time)
		await forest_shot("creek-time-%.1f"%sample_time)
	creek_mat.set_shader_parameter("review_time",1.0)
	island.camera_effects.dof_blur_near_enabled=false;island.camera_effects.dof_blur_far_enabled=false
	await forest_shot("without-dof")
	position(island.HERO_START_X)
	island.hero.sprite_frames=load("res://assets/characters/rest_rise_right/color_matched/rest_rise_color_matched.tres")
	island.hero.animation=&"rest_rise_right";island.hero.frame=0
	await forest_shot("lying")
	var f:=FileAccess.open(FOREST_REVIEW+phase+"-camera.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(checks,"  "))
	quit(0)
