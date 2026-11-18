extends SceneTree
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island)
	island.hud.hide();island.manual_control=false;island.set_process(false)
	island.set_route_sample("forest_west_light","forest_west_mid",.8);island._update_occluders(2.0)
	var layers=[]
	for node in island.get_node("World").find_children("Forest_Paint_*","MeshInstance3D",true,false):
		layers.append(node)
		var tex=node.material_override.get_shader_parameter("painting")
		var arrays=node.mesh.surface_get_arrays(0)
		print("PAINT_AUDIT ",node.name," ",tex.resource_path," ",tex.get_size()," ",node.material_override.get_shader_parameter("layer")," uv ",arrays[Mesh.ARRAY_TEX_UV][0]," ",arrays[Mesh.ARRAY_TEX_UV][-1])
	for child in island.get_children():
		if child is WorldEnvironment:child.environment.volumetric_fog_enabled=false
	island.camera.attributes.dof_blur_far_enabled=false;island.camera.attributes.dof_blur_near_enabled=false
	for variant in ["all","depth","middle","near"]:
		for layer in layers:layer.visible=variant=="all" or str(layer.name).to_lower().ends_with(variant)
		for i in 20:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg("res://artifacts/forest-layer-role-review/diagnose-"+variant+".jpg",.94)
	quit()
