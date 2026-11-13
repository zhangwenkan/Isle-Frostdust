extends "res://tools/capture_pixel_bamboo.gd"
func run_capture() -> void:
	island=load("res://scenes/island.tscn").instantiate()
	root.add_child(island);current_scene=island
	island.set_process(false);island.hero.pause();island.hud.visible=false
	control_time(island)
	freeze_material(island.atmosphere.mountain_cloud_material,"fog")
	freeze_material(island.background_comparison.original_sky,"sky")
	freeze_material(island.background_comparison.comparison_sky,"sky")
	set_time(1.0)
	var nodes=island.find_children("PixelBamboo_*","MeshInstance3D",true,false)
	assert(nodes.size()==82)
	assert(island.find_children("ForestVisibility*","MeshInstance3D",true,false).is_empty())
	var layers:Dictionary={}
	for node in nodes:
		var data:Dictionary=node.get_meta("extras",{})
		var layer:int=int(data.pixel_bamboo_layer)
		layers[layer]=int(layers.get(layer,0))+1
		var mat:ShaderMaterial=node.get_active_material(0)
		assert(is_equal_approx(float(mat.get_shader_parameter("forest_depth")),float(layer)))
		assert(mat.get_shader_parameter("pixel_atlas")!=null)
	assert(layers.size()==5)
	position(-6.8)
	await pixel_shot("wind-1")
	for node in nodes:node.get_active_material(0).set_shader_parameter("review_time",4.0)
	await pixel_shot("wind-4")
	for node in nodes:node.get_active_material(0).set_shader_parameter("review_time",1.0)
	# Check depth on the existing sprite material from the same gameplay camera.
	# These diagnostic positions do not extend the playable corridor.
	var tree:MeshInstance3D=island.find_child("PixelBamboo_L0_007",true,false)
	var point:Vector3=tree.global_position+Vector3(0,.65,0)
	var ray:Vector3=(point-island.camera.global_position).normalized()
	island.contact_shadow.visible=false
	for side in [-1.0,1.0]:
		island.hero.position=point+ray*side*1.2-Vector3(0,.65,0)
		await settle(24)
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(PIXEL_REVIEW+"depth-"+("front" if side<0 else "behind")+".png")
	island.contact_shadow.visible=true
	position(-11.0)
	var start_x:float=island.hero_x
	for i in 120:
		step_world(Vector2.RIGHT,1.0/30.0)
		await settle(1)
	assert(island.hero_x>start_x+14.0)
	for i in 60:
		step_world(Vector2.LEFT,1.0/30.0)
		await settle(1)
	var f:=FileAccess.open(PIXEL_REVIEW+"runtime-verification.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"card_count":nodes.size(),"layers":layers,"legacy_valley_absent":true,"layer_metadata_bound":true,"alpha_textures_bound":true,"rendered_walk_return_frames":180,"walk_start_x":start_x,"walk_end_x":island.hero_x,"depth_diagnostic":str(island.camera.unproject_position(point)),"video_recorded":false},"  "))
	print("PIXEL_RUNTIME_VERIFIED ",layers)
	quit(0)
