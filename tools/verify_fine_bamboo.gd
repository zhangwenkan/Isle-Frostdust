extends "res://tools/capture_fine_bamboo.gd"
func run_capture() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.visible=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	var cards=island.find_children("PixelBamboo_*","MeshInstance3D",true,false)
	assert(cards.size()==82)
	var variants:Dictionary={}
	var layers:Dictionary={}
	for node in cards:
		var data:Dictionary=node.get_meta("extras",{})
		var mat:ShaderMaterial=node.get_active_material(0)
		assert(mat.get_shader_parameter("fine_color")!=null)
		assert(mat.get_shader_parameter("surface_directions")!=null)
		assert(float(mat.get_shader_parameter("forest_depth"))==float(data.pixel_bamboo_layer))
		variants[data.fine_atlas_variant]=int(variants.get(data.fine_atlas_variant,0))+1
		layers[data.pixel_bamboo_layer]=int(layers.get(data.pixel_bamboo_layer,0))+1
	assert(variants.size()==5 and layers.size()==5)
	position(-6.8)
	await pixel_shot("wind1")
	for node in cards:node.get_active_material(0).set_shader_parameter("review_time",4.0)
	await pixel_shot("wind4")
	for node in cards:node.get_active_material(0).set_shader_parameter("review_time",1.0)
	island.atmosphere.apply(11.2,.9)
	await pixel_shot("overcast")
	island.atmosphere.apply(island.daylight_hour,island.cloud_cover)
	position(-11)
	for i in 90:
		step_world(Vector2.RIGHT,1.0/30.0)
		await settle(1)
	assert(island.hero_x>-.3)
	for i in 60:
		step_world(Vector2.LEFT,1.0/30.0)
		await settle(1)
	var f:=FileAccess.open("res://artifacts/bamboo-fine-atlas-review/runtime-verification.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"cards":cards.size(),"variants":variants,"layers":layers,"color_and_direction_maps_bound":true,"rendered_walk_return_frames":150,"final_hero_x":island.hero_x,"video_recorded":false},"  "))
	print("FINE_BAMBOO_VERIFIED ",variants)
	quit(0)
