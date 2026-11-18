extends SceneTree
func _initialize():call_deferred("run")
func run():
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1280,720)
	var island=load("res://scenes/layered_island.tscn").instantiate();root.add_child(island)
	island.manual_control=false;island.hud.hide();island.set_process(false)
	island.set_route_sample("forest_west_light","forest_west_mid",.8)
	island.camera.attributes=null
	for child in island.get_children():
		if child is WorldEnvironment:child.environment.volumetric_fog_enabled=false
	print("WORLD_BASIS ",island.get_node("World").global_transform)
	for node in island.get_node("World").find_children("*","MeshInstance3D",true,false):
		node.visible=str(node.name).begins_with("Forest_Paint_")
	var layers=island.get_node("World").find_children("Forest_Paint_*","MeshInstance3D",true,false)
	for layer in layers:
		var arr=layer.mesh.surface_get_arrays(0)
		var tex=layer.material_override.get_shader_parameter("painting")
		for uv in [Vector2(0,0),Vector2(1,1),Vector2(.5,.5)]:
			var best=0;var dist=100.0
			for i in arr[Mesh.ARRAY_TEX_UV].size():
				var d=arr[Mesh.ARRAY_TEX_UV][i].distance_to(uv)
				if d<dist:dist=d;best=i
			var world=layer.to_global(arr[Mesh.ARRAY_VERTEX][best])
			print("PROJECTION ",layer.name," UV ",arr[Mesh.ARRAY_TEX_UV][best]," WORLD ",world," SCREEN ",island.camera.unproject_position(world))
		for node in layers:node.visible=node==layer
		for i in 20:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg("res://artifacts/forest-wind-mist-review/diagnose-original-"+str(layer.name)+".jpg",.94)
		var material=ShaderMaterial.new();var shader=Shader.new()
		shader.code="shader_type spatial; render_mode unshaded,cull_disabled,fog_disabled; uniform sampler2D painting:source_color; void fragment(){ALBEDO=texture(painting,UV).rgb; ALPHA=texture(painting,UV).a;}"
		material.shader=shader;material.set_shader_parameter("painting",tex);layer.material_override=material
		for i in 20:await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg("res://artifacts/forest-wind-mist-review/diagnose-"+str(layer.name)+".jpg",.94)
	quit()
